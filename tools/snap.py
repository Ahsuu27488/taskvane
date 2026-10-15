"""Capture a window by title to PNG (dev helper): python tools/snap.py "Taskvane" out.png"""
import ctypes
import sys
from ctypes import wintypes
from PIL import Image

user32, gdi32 = ctypes.windll.user32, ctypes.windll.gdi32
user32.SetProcessDPIAware()
title, out = sys.argv[1], sys.argv[2]
hwnd = user32.FindWindowW(None, title)
if not hwnd:
    sys.exit("window not found")
r = wintypes.RECT()
user32.GetWindowRect(hwnd, ctypes.byref(r))
w, h = r.right - r.left, r.bottom - r.top
hdc = user32.GetWindowDC(hwnd)
mdc = gdi32.CreateCompatibleDC(hdc)
bmp = gdi32.CreateCompatibleBitmap(hdc, w, h)
gdi32.SelectObject(mdc, bmp)
user32.PrintWindow(hwnd, mdc, 2)  # PW_RENDERFULLCONTENT


class BIH(ctypes.Structure):
    _fields_ = [("biSize", wintypes.DWORD), ("biWidth", wintypes.LONG), ("biHeight", wintypes.LONG), ("biPlanes", wintypes.WORD),
                ("biBitCount", wintypes.WORD), ("biCompression", wintypes.DWORD), ("biSizeImage", wintypes.DWORD),
                ("biXPelsPerMeter", wintypes.LONG), ("biYPelsPerMeter", wintypes.LONG), ("biClrUsed", wintypes.DWORD), ("biClrImportant", wintypes.DWORD)]


bi = BIH(ctypes.sizeof(BIH), w, -h, 1, 32, 0, 0, 0, 0, 0, 0)
buf = ctypes.create_string_buffer(w * h * 4)
gdi32.GetDIBits(mdc, bmp, 0, h, buf, ctypes.byref(bi), 0)
Image.frombuffer("RGB", (w, h), buf, "raw", "BGRX", 0, 1).save(out)
gdi32.DeleteObject(bmp); gdi32.DeleteDC(mdc); user32.ReleaseDC(hwnd, hdc)
print(out, w, h)
