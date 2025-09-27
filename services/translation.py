from core.prompts import translation_prompts
from services import llm

SUPPORTED_LANGS = ["Korean", "English", "Vietnamese", "Chinese"]

# translation_prompts 는 한국어 <-> (영/베/중) 만 정의되어 있음
# 키 패턴: korean_to_english, english_to_korean, ...

def _build_key(src: str, tgt: str) -> str:
    return f"{src.lower()}_to_{tgt.lower()}"

def translate_any(text: str, source_language: str, target_language: str, model: str | None = None) -> str:
    """지정된 소스/타깃 언어 쌍에 대해 번역 수행.
    현재 프롬프트는 한국어가 반드시 source 또는 target 에 포함된 경우만 지원.
    동일 언어면 원문 그대로 반환.
    """
    if source_language == target_language:
        return text
    if source_language not in SUPPORTED_LANGS or target_language not in SUPPORTED_LANGS:
        raise ValueError("지원하지 않는 언어")
    key = _build_key(source_language, target_language)
    if key not in translation_prompts:
        raise ValueError(f"프롬프트 미구현 언어쌍: {source_language}->{target_language}")
    prompt = translation_prompts[key].format(text=text)
    system_role = "당신은 의미를 정확히 유지하며 자연스럽게 번역하는 전문가입니다."
    messages = [
        {"role": "system", "content": system_role},
        {"role": "user", "content": prompt},
    ]
    return llm.chat(messages, model=model)

# 하위 호환(기존 한국어→타겟)
def translate(text: str, target_language: str, model: str | None = None) -> str:
    return translate_any(text, "Korean", target_language, model=model)

def translate_text(text, target_language):  # legacy
    return translate(text, target_language)

def detect_language(text):  # 간단 플레이스홀더
    return "ko"

def translate_batch(texts, target_language):
    return [translate(t, target_language) for t in texts]

def get_supported_languages():
    return SUPPORTED_LANGS