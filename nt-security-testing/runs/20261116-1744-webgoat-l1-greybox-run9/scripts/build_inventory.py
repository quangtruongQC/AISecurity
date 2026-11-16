"""
Section 3i page/element inventory builder for WebGoat Run #9.
Enumerates every lesson under every category (from the authenticated lessonmenu.mvc
response) and, for each lesson, every assignment sub-step (from lessonoverview.mvc).
Writes evidence/page-inventory.csv: category,lesson,lesson_file,substep,method,url,status,finding_id,notes
"""
import json
import csv
import time
import requests

RUN_DIR = r"C:\AISecurity\nt-security-testing\runs\20261116-1744-webgoat-l1-greybox-run9"
BASE = "http://10.242.10.31:8007/WebGoat"

with open(fr"{RUN_DIR}\evidence\http\body-04-lessonmenu.html", encoding="utf-8") as f:
    menu = json.load(f)
with open(fr"{RUN_DIR}\evidence\http\body-08-labels.json", encoding="utf-8") as f:
    labels = json.load(f)

session = requests.Session()
r1 = session.get(f"{BASE}/login", timeout=10)
r2 = session.post(f"{BASE}/login", data={"username": "xtbuiquang", "password": "Password1@"}, timeout=10, allow_redirects=True)
assert "JSESSIONID" in session.cookies.get_dict(), "login failed, no JSESSIONID set"
print("Logged in, JSESSIONID:", session.cookies.get_dict().get("JSESSIONID"))

rows = []
lesson_count = 0
substep_count = 0

for category_node in menu:
    cat_key = category_node["name"]
    cat_label = labels.get(cat_key, cat_key)
    for lesson_node in category_node.get("children", []):
        if lesson_node["type"] != "LESSON":
            continue
        lesson_count += 1
        link = lesson_node["link"]  # "#lesson/SqlInjection.lesson"
        lesson_file = link.split("/", 1)[1]  # "SqlInjection.lesson"
        lesson_key = lesson_node["name"]
        lesson_label = labels.get(lesson_key, lesson_key)

        overview_url = f"{BASE}/service/lessonoverview.mvc/{lesson_file}"
        try:
            resp = session.get(overview_url, timeout=10)
            status_code = resp.status_code
            try:
                assignments = resp.json()
            except ValueError:
                assignments = None
        except requests.RequestException as e:
            status_code = None
            assignments = None
            print(f"ERROR fetching {overview_url}: {e}")

        if assignments:
            for a in assignments:
                substep_count += 1
                asn = a["assignment"]
                rows.append({
                    "category": cat_label,
                    "lesson": lesson_label,
                    "lesson_file": lesson_file,
                    "substep": asn["name"],
                    "method": "POST/GET (lesson-dependent)",
                    "url": asn["path"],
                    "assignment_id": asn["id"],
                    "solved_flag_at_inventory_time": a.get("solved"),
                    "status": "not tested",
                    "finding_id": "",
                    "notes": "enumerated via GET /WebGoat/service/lessonoverview.mvc/<lesson>.lesson (confirmed real endpoint, captured via browser Network panel this run)",
                })
        else:
            # Lesson has no backend "assignment" sub-steps (e.g., pure-content/intro lesson,
            # or the overview call failed) - still record it as one inventory row so it isn't silently dropped.
            rows.append({
                "category": cat_label,
                "lesson": lesson_label,
                "lesson_file": lesson_file,
                "substep": "(no assignment sub-steps returned)",
                "method": "GET",
                "url": f"#lesson/{lesson_file}",
                "assignment_id": "",
                "solved_flag_at_inventory_time": "",
                "status": "not tested",
                "finding_id": "",
                "notes": f"lessonoverview.mvc HTTP {status_code}; content-only/informational lesson step or assignment-less lesson - to be confirmed by direct navigation",
            })
        time.sleep(0.4)  # stay well under the 5 req/s guardrail, sequential only

with open(fr"{RUN_DIR}\evidence\page-inventory.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["category", "lesson", "lesson_file", "substep", "method", "url",
                                       "assignment_id", "solved_flag_at_inventory_time", "status", "finding_id", "notes"])
    w.writeheader()
    for row in rows:
        w.writerow(row)

print(f"Lessons enumerated: {lesson_count}")
print(f"Inventory rows written: {len(rows)}")
