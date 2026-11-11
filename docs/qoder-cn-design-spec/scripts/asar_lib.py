"""Minimal Electron ASAR reader: header parse, list, extract by path."""
import json
import os
import struct

ASAR = r"E:\develop-lcb\apps\Qoder CN\.qoder-versions\0.5.7\resources\app.asar"


class Asar:
    def __init__(self, path=ASAR):
        self.path = path
        with open(path, "rb") as f:
            head = f.read(16)
            json_len = struct.unpack("<I", head[12:16])[0]
            self.header = json.loads(f.read(json_len).decode("utf-8"))
        self.data_offset = 16 + json_len
        self.files = []  # (path, size, offset)
        self._walk(self.header, [])

    def _walk(self, node, parts):
        for name, child in node.get("files", {}).items():
            if "files" in child:
                self._walk(child, parts + [name])
            else:
                self.files.append(("/".join(parts + [name]), child.get("size", 0), child.get("offset")))

    def read(self, relpath):
        for p, size, off in self.files:
            if p == relpath:
                with open(self.path, "rb") as f:
                    f.seek(self.data_offset + int(off))
                    return f.read(size)
        raise KeyError(relpath)

    def extract(self, relpath, outdir):
        data = self.read(relpath)
        dest = os.path.join(outdir, relpath)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(data)
        return dest


if __name__ == "__main__":
    a = Asar()
    print("total files:", len(a.files))
    print("total bytes:", sum(s for _, s, _ in a.files))
