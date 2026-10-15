"""All-process snapshot in one syscall via NtQuerySystemInformation(SystemProcessInformation).

This is how Task Manager gets its numbers, and it's ~50x cheaper than opening every
process with psutil each refresh. Offsets are for the 64-bit SYSTEM_PROCESS_INFORMATION.
"""
import ctypes
import struct

_ntdll = ctypes.WinDLL("ntdll")
_NtQSI = _ntdll.NtQuerySystemInformation
_NtQSI.argtypes = [ctypes.c_ulong, ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong)]
_NtQSI.restype = ctypes.c_long

SystemProcessInformation = 5
STATUS_INFO_LENGTH_MISMATCH = ctypes.c_long(0xC0000004).value

_buf_size = 1 << 20
_buf = ctypes.create_string_buffer(_buf_size)


def snapshot():
    """Return {pid: dict} with cumulative CPU time (100ns units) and current counters."""
    global _buf, _buf_size
    needed = ctypes.c_ulong()
    while True:
        st = _NtQSI(SystemProcessInformation, _buf, _buf_size, ctypes.byref(needed))
        if st == STATUS_INFO_LENGTH_MISMATCH:
            _buf_size = max(needed.value + (256 << 10), _buf_size * 2)
            _buf = ctypes.create_string_buffer(_buf_size)
            continue
        if st != 0:
            raise OSError(f"NtQuerySystemInformation failed: 0x{st & 0xFFFFFFFF:08X}")
        break

    raw = _buf.raw
    base = ctypes.addressof(_buf)
    out = {}
    off = 0
    while True:
        (next_off, threads, private_ws) = struct.unpack_from("<IIq", raw, off)
        create, user, kernel = struct.unpack_from("<qqq", raw, off + 32)
        name_len, _maxlen = struct.unpack_from("<HH", raw, off + 56)
        name_ptr, = struct.unpack_from("<Q", raw, off + 64)
        pid, ppid = struct.unpack_from("<QQ", raw, off + 80)
        handles, session = struct.unpack_from("<II", raw, off + 96)
        ws, = struct.unpack_from("<Q", raw, off + 144)
        private_bytes, = struct.unpack_from("<Q", raw, off + 184)
        r_bytes, w_bytes, o_bytes = struct.unpack_from("<qqq", raw, off + 232)
        if name_ptr and name_len:
            s = name_ptr - base
            name = raw[s:s + name_len].decode("utf-16-le", "replace")
        else:
            name = "System Idle Process" if pid == 0 else ""
        out[pid] = {
            "pid": pid, "ppid": ppid, "name": name, "threads": threads, "handles": handles, "session": session,
            "cpu_time": user + kernel, "created": create, "mem": private_ws, "ws": ws, "private": private_bytes,
            "io_total": r_bytes + w_bytes,  # like Task Manager: excludes "other" (non-read/write) I/O
        }
        if not next_off:
            break
        off += next_off
    return out
