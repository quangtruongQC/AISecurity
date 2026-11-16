import csv

PATH = r"C:\AISecurity\nt-security-testing\runs\20261116-1744-webgoat-l1-greybox-run9\evidence\page-inventory.csv"

with open(PATH, encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
fieldnames = list(rows[0].keys())

for r in rows:
    if r["lesson_file"] == "WebWolfIntroduction.lesson":
        r["status"] = "not applicable - out of scope"
        r["notes"] = ('WebWolf is explicitly out-of-scope per Section 1 ("not in scope unless explicitly added"); '
                       "this sub-step requires interacting with the WebWolf companion service and will not be actively tested.")

with open(PATH, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)

print("patched")
