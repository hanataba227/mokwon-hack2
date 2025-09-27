from core.prompts import style_transformation_prompts
from services import llm

def transform(text: str, style_type: str, model: str | None = None) -> str:
    """한국어 텍스트의 문체를 변환합니다.
    
    Args:
        text: 변환할 한국어 텍스트
        style_type: 변환할 문체 ('Formal', 'Informal', 'Basic Vocabulary', 'Hanja')
        model: 사용할 LLM 모델명 (None이면 기본값)
    
    Returns:
        문체가 변환된 텍스트
    
    Raises:
        ValueError: 지원하지 않는 스타일 타입일 경우
    """
    # style_type이 dict로 전달될 수 있으므로 label 추출 허용
    if isinstance(style_type, dict):
        style_label = style_type.get("label")
    else:
        style_label = style_type

    if not isinstance(style_label, str):
        raise ValueError(f"지원하지 않는 스타일 형식: {style_type!r}")

    # 정규화: 소문자화, 언더스코어를 공백으로 변환
    norm = style_label.strip().lower().replace("_", " ")

    # 매핑: 정규화된 라벨(lowercase, underscores->spaces) -> prompts의 키
    mapping = {
        "formal": "Formal",
        "informal": "Informal",
        "basic vocabulary": "Basic_Vocabulary",
        "hanja": "Hanja",
        "narrative": "Narrative",
        "descriptive": "Descriptive",
    }

    prompt_key = mapping.get(norm)
    if not prompt_key:
        raise ValueError(f"지원하지 않는 스타일: {style_label}. 지원 스타일: {list(mapping.keys())}")

    prompt = style_transformation_prompts[prompt_key].format(text=text)
    messages = [
        {"role": "system", "content": "당신은 의미 왜곡 없이 문체만 조정하는 한국어 문체 전문가입니다."},
        {"role": "user", "content": prompt},
    ]
    return llm.chat(messages, model=model)

# 하위 호환성을 위한 별칭 (app.py에서 사용 중)
transform_style = transform