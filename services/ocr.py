from __future__ import annotations

import io
import os
from typing import Union

try:
	from PIL import Image
except Exception: 
	Image = None

try:
	import openai
except Exception:
	openai = None
try:
	from openai import OpenAI as OpenAIClient
except Exception:
	OpenAIClient = None


def _read_image_bytes(uploaded: Union[bytes, "io.BufferedReader", str]) -> bytes:
	"""업로드된 파일 또는 파일 경로로부터 원시 바이트를 반환합니다."""
	# 파일 경로인 경우
	if isinstance(uploaded, str):
		with open(uploaded, "rb") as f:
			return f.read()

	# 이미 바이트인 경우
	if isinstance(uploaded, (bytes, bytearray)):
		return bytes(uploaded)

	# 그 외에는 파일처럼 읽을 수 있는 객체(Streamlit UploadedFile 등)로 간주
	if hasattr(uploaded, "read"):
		# 가능한 경우 파일 포인터를 맨 앞으로 되돌림
		try:
			uploaded.seek(0)
		except Exception:
			pass
		return uploaded.read()

	raise TypeError("OCR에 지원되지 않는 업로드 타입입니다: 파일유사객체, bytes, 또는 경로 문자열이어야 합니다")


def extract_text_from_image(uploaded: Union[bytes, "io.BufferedReader", str]) -> str:
	"""이미지에서 텍스트를 추출하고(선택적으로) OpenAI로 후처리합니다.
	Args:
		uploaded: Streamlit 업로드 파일(읽기 가능), 바이트, 또는 파일 경로.
	Returns:
		이미지에서 추출된 텍스트(후처리된 텍스트). 텍스트가 없으면 빈 문자열을 반환할 수 있습니다.
	Raises:
		RuntimeError: 이미지 처리에 필요한 라이브러리나 OCR 백엔드가 없는 경우 발생합니다.
	"""
	raw = _read_image_bytes(uploaded)

	if Image is None:
		raise RuntimeError("이미지 처리를 위해 Pillow가 필요합니다. 'pip install Pillow'로 설치하세요.")

	# 이미지 열기
	try:
		img = Image.open(io.BytesIO(raw))
		# 일부 포맷에서 문제를 피하기 위해 RGB로 변환
		if img.mode in ("RGBA", "P"):
			img = img.convert("RGB")
	except Exception as e:
		raise RuntimeError(f"OCR을 위해 이미지를 열지 못했습니다: {e}")

	# GPT API 전용으로 OCR 수행
	if openai is None or not os.environ.get("OPENAI_API_KEY"):
		raise RuntimeError(
			"OpenAI API 키가 설정되어 있지 않거나 openai 패키지가 없습니다. GPT 기반 OCR을 사용하려면 'openai' 패키지를 설치하고 OPENAI_API_KEY를 설정하세요."
		)

	# 이미지 바이트를 base64로 인코딩하여 데이터 URI 형태로 모델에 전달
	try:
		import base64

		img_format = getattr(img, "format", None) or "png"
		b64 = base64.b64encode(raw).decode("ascii")
		data_uri = f"data:image/{img_format.lower()};base64,{b64}"
	except Exception as e:
		raise RuntimeError(f"이미지 인코딩 중 오류 발생: {e}")

	cleaned = ""
	try:
		if OpenAIClient is None:
			raise RuntimeError("openai.OpenAI client가 설치되어 있지 않습니다. 'pip install openai'로 설치하세요.")

		if not os.environ.get("OPENAI_API_KEY"):
			raise RuntimeError("환경변수 OPENAI_API_KEY가 설정되어 있지 않습니다.")

		client = OpenAIClient()

		# 한 번의 Responses API 호출로 이미지에서 텍스트 추출 및 정리 수행
		response = client.responses.create(
			model="gpt-4o-mini",
			input=[{
				"role": "user",
				"content": [
					{"type": "input_text", "text": "이미지에서 텍스트를 추출하고, OCR 오류를 정리하여 정리된 텍스트만 반환하세요."},
					{"type": "input_image", "image_url": data_uri},
				],
			}],
		)

		# Responses API의 편리한 속성(output_text)을 우선 사용
		cleaned = getattr(response, "output_text", None) or ""

		# output_text가 비어있으면 response.output 구조에서 텍스트 조합
		if not cleaned:
			parts = []
			for out_item in getattr(response, "output", []) or []:
				for c in out_item.get("content", []):
					if c.get("type") == "output_text":
						parts.append(c.get("text", ""))
			cleaned = "\n".join(parts).strip()

	except Exception as e:
		raise RuntimeError(f"OpenAI OCR 처리 중 오류 발생: {e}")

	return cleaned
