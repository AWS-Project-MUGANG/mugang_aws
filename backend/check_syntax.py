with open("main.py", encoding="utf-8") as f:
    lines = f.readlines()

# 758번 줄 주변 확인
for i in range(754, 765):
    print(f"{i+1:4d}: {repr(lines[i])}")
