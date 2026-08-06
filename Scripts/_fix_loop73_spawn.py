from pathlib import Path
import ast

p = Path(r"D:\Skyguard52\Scripts\build_skyguard_aaa_loop73_true_art_slice16_capture.py")
lines = p.read_text(encoding="utf-8").splitlines()
fixed = []
i = 0
while i < len(lines):
    line = lines[i]
    if (
        "TA16_NS_PropWashAuth" in line
        and i + 1 < len(lines)
        and "NS_L73_MuzzleBurst" in lines[i + 1]
    ):
        fixed.append(
            '            spawn_niagara(PREFIX + "TA16_NS_PropWashAuth_%s" % name, (bx + 3.76, cy + 0.02, cz + 0.02), "NS_L73_PropWashAuth", (0.18, 0.18, 0.18), bound=True)'
        )
        i += 2
        continue
    fixed.append(line)
    i += 1
text = "\n".join(fixed) + "\n"
ast.parse(text)
p.write_text(text, encoding="utf-8")
print("FIXED", p.stat().st_size)
for idx, line in enumerate(text.splitlines(), 1):
    if 1654 <= idx <= 1662:
        print(f"{idx}:{line}")
