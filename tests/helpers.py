import base64

# Fake JPEG bytes — not a real image, but valid for round-trip base64 testing
FAKE_JPEG = b"\xff\xd8\xff\xe0FAKEJPEGDATA\xff\xd9"
FAKE_JPEG_B64 = base64.b64encode(FAKE_JPEG).decode()

SAMPLE_HTML = f"""<!DOCTYPE html><html><body>
<div data-ad-preview=message>
  <span dir=auto>人間底是無波處，一日風波十二時！</span>
  <img data-imgperflogname=feedImage src="data:image/jpeg;base64,{FAKE_JPEG_B64}">
</div>
<div data-ad-preview=message>
  <span dir=auto>春風又綠江南岸，明月何時照我還。</span>
  <img data-imgperflogname=feedImage src="data:image/jpeg;base64,{FAKE_JPEG_B64}">
  <img data-imgperflogname=feedImage src="data:image/jpeg;base64,{FAKE_JPEG_B64}">
</div>
<div data-ad-preview=message>
  <span dir=auto>設定</span>
</div>
</body></html>"""
