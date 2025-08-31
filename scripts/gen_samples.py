import os, csv
from pathlib import Path

root = Path(__file__).resolve().parent.parent
samples = root / "samples"
samples.mkdir(parents=True, exist_ok=True)

# 1) demo.csv — tiny dataset
with open(samples / "demo.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "name", "price"])
    w.writerow([1, "pen", 1.20])
    w.writerow([2, "notebook", 2.50])
    w.writerow([3, "ruler", 0.99])

# 2) quotes.csv — embedded commas/quotes/newlines
with open(samples / "quotes.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "text"])
    w.writerow([1, "He said, \"hello, world\"\nNext line."])
    w.writerow([2, "Comma, inside, field"])

# 3) latin1.csv — ISO-8859-1
latin1 = "id,name\n1,café\n2,mañana\n3,über\n"
with open(samples / "latin1.csv", "w", newline="") as f:
    f.write(latin1.encode("latin-1", errors="ignore").decode("latin-1"))

# 4) demo.xlsx — minimal sheet via openpyxl (created later after deps installed)
try:
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    ws.append(["A", "B", "C"])
    ws.append(["alpha", 1, 1.1])
    ws.append(["beta", 2, 2.2])
    wb.save(samples / "demo.xlsx")
except Exception:
    # We'll create this after we install wheels; script can be re-run.
    print("(note) openpyxl not installed yet — run again after install to create demo.xlsx")

print("Created sample files in", samples)
