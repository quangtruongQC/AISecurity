/**
 * OpenCRE API Client
 *
 * Fetches ASVS requirement mappings from OpenCRE (Open Common Requirement Enumeration)
 * to provide transitive mappings to ISO 27001 and other standards.
 *
 * API Documentation: https://www.opencre.org/rest/v1/
 * GitHub: https://github.com/OWASP/OpenCRE
 */
interface ISO27001Mapping {
    sectionID: string;
    section: string;
    via_cre: string;
}
export declare class OpenCREClient {
    private static readonly BASE_URL;
    private static readonly REQUEST_TIMEOUT;
    private static readonly CACHE_TTL;
    private cache;
    private lastRequestTime;
    private minRequestInterval;
    /**
     * Get ISO 27001 mappings for an ASVS requirement via OpenCRE
     *
     * Process:
     * 1. Fetch ASVS requirement from OpenCRE
     * 2. Get linked CREs
     * 3. For each CRE, fetch its links
     * 4. Extract ISO 27001 mappings
     */
    getISO27001Mappings(asvsId: string): Promise<ISO27001Mapping[]>;
    /**
     * Fetch ASVS requirement data from OpenCRE
     */
    private fetchASVSRequirement;
    /**
     * Fetch CRE data by ID
     */
    private fetchCRE;
    /**
     * Fetch with rate limiting to be nice to OpenCRE API
     */
    private fetchWithRateLimit;
    /**
     * Get data from cache if not expired
     */
    private getFromCache;
    /**
     * Store data in cache
     */
    private setCache;
    /**
     * Remove duplicate ISO 27001 mappings
     */
    private deduplicateMappings;
    /**
     * Clear the cache (useful for testing or manual refresh)
     */
    clearCache(): void;
    /**
     * Get cache statistics
     */
    getCacheStats(): {
        size: number;
        keys: string[];
    };
}
export {};
