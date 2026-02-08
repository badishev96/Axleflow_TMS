import re
from pathlib import Path

p = Path("app/api/v1/app_page.py")
t = p.read_text(encoding="utf-8")

pattern = r"def parse_dt\(s: str\):[\s\S]*?return datetime\.strptime\(s, \"%Y-%m-%d %H:%M\"\)"

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

new_t, n = re.subn(pattern, replacement, t, count=1)
if n == 0:
    print("ERROR: parse_dt block not found")
    raise SystemExit(1)

p.write_text(new_t, encoding="utf-8")
print("OK: parse_dt updated")

