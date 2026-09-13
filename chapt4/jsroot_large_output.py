"""Lossless large-object transport for ROOT 6.40 Jupyter's native JSROOT output.

TBufferJSON.zipJSON can return an empty string above its single-block limit.
Use standard ROOT zlib blocks for those payloads. This does not modify the
canvas JSON, histogram bins, errors, display options, or notebook MIME bundle.
The override is confined to the current kernel; no installed files are edited.
"""
import base64
import zlib
import ROOT

def enable():
    if getattr(ROOT.TBufferJSON, '_course_chunked_zip', False):
        return
    original = ROOT.TBufferJSON.zipJSON

    def zip_json(text):
        raw = str(text).encode('utf-8')
        if len(raw) < 8 * 1024 * 1024:
            return original(text)
        blocks = []
        for offset in range(0, len(raw), 8 * 1024 * 1024):
            part = raw[offset:offset + 8 * 1024 * 1024]
            compressed = zlib.compress(part, 9)
            header = b'ZL\x08' + len(compressed).to_bytes(3, 'little') + len(part).to_bytes(3, 'little')
            blocks.append(header + compressed)
        return base64.b64encode(b''.join(blocks)).decode('ascii')

    ROOT.TBufferJSON.zipJSON = staticmethod(zip_json)
    ROOT.TBufferJSON._course_chunked_zip = True
