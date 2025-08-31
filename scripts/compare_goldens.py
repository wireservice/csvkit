import difflib, sys, pathlib

pairs = [
    ("out/csvstat_demo.txt", "tests/goldens/csvstat_demo.txt"),
    ("out/csvcut_cols.txt", "tests/goldens/csvcut_cols.txt"),
    ("out/csvgrep_price.txt", "tests/goldens/csvgrep_price.txt"),
    ("out/in2csv_xlsx.txt", "tests/goldens/in2csv_xlsx.txt"),
    ("out/csvsort_price.txt", "tests/goldens/csvsort_price.txt"),
]

status = 0
for out_path, golden_path in pairs:
    o = pathlib.Path(out_path).read_text(encoding="utf-8").splitlines()
    g = pathlib.Path(golden_path).read_text(encoding="utf-8").splitlines()
    if o != g:
        print(f"-- DIFF {out_path} vs {golden_path} --")
        for line in difflib.unified_diff(g, o, fromfile=golden_path, tofile=out_path, lineterm=""):
            print(line)
        status = 1

if status == 0:
    print("COMPARE_OK")
sys.exit(status)
