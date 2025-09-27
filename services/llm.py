from typing import Dict, List, Optional
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
        model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
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