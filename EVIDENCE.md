\# Evidence – csvkit local offline setup (Windows + Docker)



\## Environment

\- OS: (e.g., Windows 11 23H2)

\- Python: 3.11.9 (local venv)

\- Shell: Windows CMD

\- Branch: `docs/local-dev`

\- Commit SHAs: base `b291a10`,

\## Local offline install

\- Installed from `vendor\\wheels` with `--no-index --find-links` 

\- `csvcut --version` → `2.1.0` 

\- Demo captured to `out/` and copied to `tests/goldens/`

\- `python scripts\\compare\_goldens.py` → \*\*COMPARE\_OK\*\* 



\## Container (offline) checks

\- Image: `csvkit-offline` (Python 3.12-slim)

\- PATH (inside): `/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin`

\- `which csvcut` → `/usr/local/bin/csvcut`

\- `csvcut --version` → `2.1.0`

\- First 3 lines of sample:



id,name,price

&nbsp;1,pen,1.2

&nbsp;2,notebook,2.5

\- `csvstat /app/samples/demo.csv | head -n 6` (excerpt):



"id"

&nbsp;Type of data: Number

&nbsp;Contains null values: False

&nbsp;Non-null values: 3

&nbsp;Unique values: 3



