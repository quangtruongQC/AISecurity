import json
from collections import Counter

with open(r"C:\AISecurity\nt-security-testing\runs\20261116-1744-webgoat-l1-greybox-run9\evidence\asvs-l1-raw-mcp-export.json", encoding="utf-8") as f:
    data = json.load(f)

reqs = data["requirements"]
print("total:", len(reqs))

cat_counts = Counter(r["category"] for r in reqs)
for cat, count in sorted(cat_counts.items()):
    print(f"{count:4d}  {cat}")

print()
sub_counts = Counter((r["category"], r.get("subcategory", "")) for r in reqs)
for (cat, sub), count in sorted(sub_counts.items()):
    print(f"{count:4d}  {cat} / {sub}")
