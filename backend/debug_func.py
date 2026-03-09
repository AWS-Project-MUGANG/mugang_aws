import sys

with open("main.py", "rb") as f:
    raw = f.read()

content = raw.decode("utf-8", errors="replace")

start_idx = content.find('def _get_active_schedule(db: Session):')
snippet = content[start_idx:start_idx+2000]

with open("debug_output.txt", "w", encoding="utf-8") as out:
    for i, line in enumerate(snippet.split('\r\n')):
        out.write(f"{i+168:4d}: {line}\n")

print("Written to debug_output.txt")
