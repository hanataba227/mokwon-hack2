from core.prompts import style_transformation_prompts
from services import llm

_STYLE_KEY_MAP = {
    "Formal": "formal",
    "Informal": "informal",
    "Basic Vocabulary": "basic_vocabulary",
    "Hanja": "hanja",
    "formal": "formal",
    "informal": "informal",
    "basic_vocabulary": "basic_vocabulary",
    "hanja": "hanja",
}

def transform(text: str, style_type: str, model: str | None = None) -> str:
    key = _STYLE_KEY_MAP.get(style_type)
    if not key:
        raise ValueError(f"지원하지 않는 스타일: {style_type}")
    prompt = style_transformation_prompts[key].format(text=text)
    messages = [
        {"role": "system", "content": "당신은 의미 왜곡 없이 문체만 조정하는 한국어 문체 전문가입니다."},
        {"role": "user", "content": prompt},
    ]
    return llm.chat(messages, model=model)

def transform_style(text, style_type):  # 호환용
    return transform(text, style_type)

def get_modified_words(original_text, transformed_text):
    return []  # TODO

def provide_word_info(word):
    return {"meaning": "의미 (플레이스홀더)", "part_of_speech": "품사 (플레이스홀더)", "example": "예문 (플레이스홀더)"}