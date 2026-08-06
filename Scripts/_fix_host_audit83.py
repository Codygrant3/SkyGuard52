from pathlib import Path
p = Path(r'D:\Skyguard52\Scripts\host_audit_loop83.py')
t = p.read_text(encoding='utf-8')
# Fix leftover L82 globs and key prefixes from incomplete retarget
t2 = t.replace('AAA_Cam_L82_', 'AAA_Cam_L83_')
# also fix any remaining plain L82 cam references in report short names
# Keep AAA_L83 base paths already correct
if t2 == t:
    print('no L82 cam prefix found?')
else:
    print('retargeted AAA_Cam_L82_ -> AAA_Cam_L83_ count', t.count('AAA_Cam_L82_'))
p.write_text(t2, encoding='utf-8')
print('remaining L82 cam', t2.count('AAA_Cam_L82_'))
print('L83 cam refs', t2.count('AAA_Cam_L83_'))
