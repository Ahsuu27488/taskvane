"""Write build/version_info.txt (PyInstaller --version-file) from app.py's VERSION. Prints the version."""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
version = re.search(r'^VERSION = "([\d.]+)"', open(os.path.join(ROOT, "app.py"), encoding="utf-8").read(), re.M).group(1)
parts = (version.split(".") + ["0"] * 4)[:4]
t = ", ".join(parts)
os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
with open(os.path.join(ROOT, "build", "version_info.txt"), "w", encoding="utf-8") as f:
    f.write(f"""VSVersionInfo(
  ffi=FixedFileInfo(filevers=({t}), prodvers=({t}), mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)),
  kids=[
    StringFileInfo([StringTable('040904B0', [
      StringStruct('CompanyName', 'Taskvane'),
      StringStruct('FileDescription', 'Taskvane'),
      StringStruct('FileVersion', '{version}'),
      StringStruct('InternalName', 'Taskvane'),
      StringStruct('OriginalFilename', 'Taskvane.exe'),
      StringStruct('ProductName', 'Taskvane'),
      StringStruct('ProductVersion', '{version}')])]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
""")
print(version)
