from core.prompts import translation_prompts
from services import llm

SUPPORTED_LANGS = ["Korean", "English", "Vietnamese", "Chinese", "Japanese"]

def _build_key(src: str, tgt: str) -> str:
    """번역 프롬프트 키 생성 (소문자_to_소문자 형식)"""
    return f"{src.lower()}_to_{tgt.lower()}"

def translate_any(text: str, source_language: str, target_language: str, model: str | None = None) -> str:
    """지정된 소스/타깃 언어 쌍에 대해 번역 수행.
    Args:
        text: 번역할 텍스트
        source_language: 원본 언어 ("Korean", "English", "Vietnamese", "Chinese", "Japanese")
        target_language: 타깃 언어 ("Korean", "English", "Vietnamese", "Chinese", "Japanese")
        model: 사용할 LLM 모델명 (None이면 기본값)
    Returns:
        번역된 텍스트
    Raises:
        ValueError: 지원하지 않는 언어 또는 프롬프트가 없는 언어쌍일 경우
    Note:
        현재 프롬프트는 한국어가 반드시 source 또는 target에 포함된 경우만 지원.
        동일 언어면 원문 그대로 반환.
    """
    if source_language == target_language:
        return text
        
    if source_language not in SUPPORTED_LANGS or target_language not in SUPPORTED_LANGS:
        raise ValueError(f"지원하지 않는 언어: {source_language} -> {target_language}")
        
    key = _build_key(source_language, target_language)
    if key not in translation_prompts:
        raise ValueError(f"프롬프트 미구현 언어쌍: {source_language} -> {target_language}")
        
    prompt = translation_prompts[key].format(text=text)
    system_role = "당신은 의미를 정확히 유지하며 자연스럽게 번역하는 전문가입니다."
    messages = [
        {"role": "system", "content": system_role},
        {"role": "user", "content": prompt},
    ]
    return llm.chat(messages, model=model)

def translate(text: str, target_language: str, model: str | None = None) -> str:
    """한국어에서 타깃 언어로 번역 (하위 호환성)"""
    return translate_any(text, "Korean", target_language, model=model)