import re
from pathlib import Path

p = Path("app/api/v1/app_page.py")
t = p.read_text(encoding="utf-8")

# Replace the entire parse_dt function with a flexible version
pattern = r"def parse_dt\(s: str\):\n(?:\s+.*\n)+?\s*return datetime\.strptime\(s, \"%Y-%m-%d %H:%M\"\)\n"
replacement = """def parse_dt(s: str):
        s = (s or "").strip()
        fmts = [
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M",
            "%m/%d/%y",
            "%m/%d/%y %I:%M %p",
        ]
        for f in fmts:
            try:
                dt = datetime.strptime(s, f)
                if f in ["%Y-%m-%d", "%m/%d/%y"]:
                    return datetime(dt.year, dt.month, dt.day, 0, 0)
                return dt
            except ValueError:
                pass
        raise ValueError("Invalid date. Use M/D/YY (optional time) or YYYY-MM-DD (optional time). Examples: 2/5/25 or 2/5/25 8:00 AM or 2026-02-07")
"""

new_t, n = re.subn(pattern, replacement, t, flags=re.MULTILINE)
if n == 0:
    print("ERROR: Could not find the old parse_dt() block to replace.")
    raise SystemExit(1)

p.write_text(new_t, encoding="utf-8")
print("OK: parse_dt() updated to flexible formats.")
