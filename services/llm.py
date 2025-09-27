from typing import Any, Dict, List, Optional
import os
import base64
from openai import OpenAI
from openai import BadRequestError

_client: Optional[OpenAI] = None


def get_client() -> OpenAI:
    """OpenAI 클라이언트 싱글턴 반환."""
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def chat(messages: List[Dict[str, str]], model: str | None = None, temperature: float = 0.7) -> str:
    """Chat Completions API 호출.

    일부 경량 모델은 temperature 파라미터 미지원(400 unsupported_value) 오류를 발생시킬 수 있으므로
    1차 시도 실패 시 temperature 제거 후 재시도한다.
    """
    if model is None:
        model = os.getenv("OPENAI_CHAT_MODEL", "gpt-5-mini")
    client = get_client()

    # 1차 시도: 제공된 temperature 사용
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        return resp.choices[0].message.content.strip()
    except BadRequestError as e:
        msg = str(e).lower()
        # temperature 관련 미지원이면 파라미터 제거 후 재시도
        if 'temperature' in msg and 'unsupported' in msg:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
            )
            return resp.choices[0].message.content.strip()
        raise


def completion(prompt: str, model: str | None = None, max_tokens: int = 256, temperature: float = 0.7) -> str:
    """(필요 시) 구 텍스트 완성 모델 대체용. Chat 모델 프롬프트로 감싸 재사용 권장."""
    system = "너는 간결하게 답변하는 도우미다."
    user = prompt
    return chat([
        {"role": "system", "content": system},
        {"role": "user", "content": user}
    ], model=model, temperature=temperature)


def vision_extract_bytes(image_bytes: bytes, prompt: str = "이미지 안의 한국어 텍스트를 그대로 추출해줘.", model: str | None = None) -> str:
    """Responses 멀티모달 API 이용한 OCR 유사 추출."""
    if model is None:
        model = os.getenv("OPENAI_VISION_MODEL", "gpt-5-mini")
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    client = get_client()
    resp = client.responses.create(
        model=model,
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_image", "image": {"b64_json": b64}}
            ]
        }]
    )
    return getattr(resp, "output_text", "").strip()


def vision_extract_file(image_path: str, prompt: str = "이미지 안의 한국어 텍스트를 그대로 추출해줘.") -> str:
    with open(image_path, "rb") as f:
        return vision_extract_bytes(f.read(), prompt=prompt)