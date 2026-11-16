import json

with open(r"C:\AISecurity\nt-security-testing\runs\20261116-1744-webgoat-l1-greybox-run9\evidence\asvs-l1-raw-mcp-export.json", encoding="utf-8") as f:
    data = json.load(f)

reqs = data["requirements"]
reqs.sort(key=lambda r: (r["category"], r.get("subcategory", ""), r["id"]))

out_path = r"C:\AISecurity\nt-security-testing\runs\20261116-1744-webgoat-l1-greybox-run9\scripts\asvs_full_listing.txt"
with open(out_path, "w", encoding="utf-8") as out:
    for r in reqs:
        out.write(f"{r['id']} | {r['category']} | {r.get('subcategory','')}\n")
        out.write(f"  {r['description']}\n\n")

print("wrote", out_path)
