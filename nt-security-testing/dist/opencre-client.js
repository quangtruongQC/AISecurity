/**
 * OpenCRE API Client
 *
 * Fetches ASVS requirement mappings from OpenCRE (Open Common Requirement Enumeration)
 * to provide transitive mappings to ISO 27001 and other standards.
 *
 * API Documentation: https://www.opencre.org/rest/v1/
 * GitHub: https://github.com/OWASP/OpenCRE
 */
import fetch from 'node-fetch';
export class OpenCREClient {
    static BASE_URL = 'https://www.opencre.org/rest/v1';
    static REQUEST_TIMEOUT = 10000; // 10 seconds
    static CACHE_TTL = 24 * 60 * 60 * 1000; // 24 hours
    // Simple in-memory cache
    cache = new Map();
    // Rate limiting
    lastRequestTime = 0;
    minRequestInterval = 100; // 100ms between requests
    /**
     * Get ISO 27001 mappings for an ASVS requirement via OpenCRE
     *
     * Process:
     * 1. Fetch ASVS requirement from OpenCRE
     * 2. Get linked CREs
     * 3. For each CRE, fetch its links
     * 4. Extract ISO 27001 mappings
     */
    async getISO27001Mappings(asvsId) {
        try {
            const mappings = [];
            // Get ASVS requirements to find CRE links
            const asvsData = await this.fetchASVSRequirement(asvsId);
            if (!asvsData || !asvsData.links) {
                return [];
            }
            // Extract CRE links
            const creLinks = asvsData.links.filter((link) => link.document.doctype === 'CRE');
            // For each CRE, get its ISO 27001 mappings
            for (const creLink of creLinks) {
                if (!creLink.document.id)
                    continue;
                const creData = await this.fetchCRE(creLink.document.id);
                if (creData && creData.links) {
                    const iso27001Links = creData.links.filter((link) => link.document.name === 'ISO 27001' &&
                        link.document.sectionID);
                    for (const isoLink of iso27001Links) {
                        mappings.push({
                            sectionID: isoLink.document.sectionID,
                            section: isoLink.document.section || '',
                            via_cre: creLink.document.id
                        });
                    }
                }
            }
            return this.deduplicateMappings(mappings);
        }
        catch (error) {
            console.error(`Failed to get ISO 27001 mappings for ${asvsId}:`, error);
            return [];
        }
    }
    /**
     * Fetch ASVS requirement data from OpenCRE
     */
    async fetchASVSRequirement(asvsId) {
        const cacheKey = `asvs:${asvsId}`;
        // Check cache first
        const cached = this.getFromCache(cacheKey);
        if (cached)
            return cached;
        try {
            // Query OpenCRE for ASVS standards
            const url = `${OpenCREClient.BASE_URL}/standard/ASVS?page=1&limit=1000`;
            const response = await this.fetchWithRateLimit(url);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            const data = await response.json();
            if (!data.standards) {
                return null;
            }
            // Find the specific ASVS requirement
            const requirement = data.standards.find((std) => std.sectionID === asvsId);
            if (requirement) {
                this.setCache(cacheKey, requirement);
            }
            return requirement || null;
        }
        catch (error) {
            console.error(`Failed to fetch ASVS requirement ${asvsId}:`, error);
            return null;
        }
    }
    /**
     * Fetch CRE data by ID
     */
    async fetchCRE(creId) {
        const cacheKey = `cre:${creId}`;
        // Check cache first
        const cached = this.getFromCache(cacheKey);
        if (cached)
            return cached;
        try {
            const url = `${OpenCREClient.BASE_URL}/id/${creId}`;
            const response = await this.fetchWithRateLimit(url);
            if (!response.ok) {
                if (response.status === 404) {
                    return null; // CRE not found
                }
                throw new Error(`HTTP ${response.status}`);
            }
            const data = await response.json();
            if (data.data) {
                this.setCache(cacheKey, data.data);
                return data.data;
            }
            return null;
        }
        catch (error) {
            console.error(`Failed to fetch CRE ${creId}:`, error);
            return null;
        }
    }
    /**
     * Fetch with rate limiting to be nice to OpenCRE API
     */
    async fetchWithRateLimit(url) {
        // Simple rate limiting
        const now = Date.now();
        const timeSinceLastRequest = now - this.lastRequestTime;
        if (timeSinceLastRequest < this.minRequestInterval) {
            await new Promise(resolve => setTimeout(resolve, this.minRequestInterval - timeSinceLastRequest));
        }
        this.lastRequestTime = Date.now();
        // Fetch with timeout
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), OpenCREClient.REQUEST_TIMEOUT);
        try {
            const response = await fetch(url, {
                signal: controller.signal,
                headers: {
                    'User-Agent': 'OWASP-ASVS-MCP-Server/1.0'
                }
            });
            clearTimeout(timeout);
            return response;
        }
        catch (error) {
            clearTimeout(timeout);
            throw error;
        }
    }
    /**
     * Get data from cache if not expired
     */
    getFromCache(key) {
        const cached = this.cache.get(key);
        if (!cached)
            return null;
        const age = Date.now() - cached.timestamp;
        if (age > OpenCREClient.CACHE_TTL) {
            this.cache.delete(key);
            return null;
        }
        return cached.data;
    }
    /**
     * Store data in cache
     */
    setCache(key, data) {
        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });
    }
    /**
     * Remove duplicate ISO 27001 mappings
     */
    deduplicateMappings(mappings) {
        const seen = new Set();
        const unique = [];
        for (const mapping of mappings) {
            if (!seen.has(mapping.sectionID)) {
                seen.add(mapping.sectionID);
                unique.push(mapping);
            }
        }
        return unique;
    }
    /**
     * Clear the cache (useful for testing or manual refresh)
     */
    clearCache() {
        this.cache.clear();
    }
    /**
     * Get cache statistics
     */
    getCacheStats() {
        return {
            size: this.cache.size,
            keys: Array.from(this.cache.keys())
        };
    }
}
