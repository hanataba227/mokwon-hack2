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
    # 스타일 키 정규화
    style_key_map = {
        "Formal": "formal",
        "Informal": "informal", 
        "Basic Vocabulary": "basic_vocabulary",
        "Hanja": "hanja"
    }
    
    key = style_key_map.get(style_type)
    if not key:
        raise ValueError(f"지원하지 않는 스타일: {style_type}. 지원 스타일: {list(style_key_map.keys())}")
    
    prompt = style_transformation_prompts[key].format(text=text)
    messages = [
        {"role": "system", "content": "당신은 의미 왜곡 없이 문체만 조정하는 한국어 문체 전문가입니다."},
        {"role": "user", "content": prompt},
    ]
    return llm.chat(messages, model=model)

# 하위 호환성을 위한 별칭 (app.py에서 사용 중)
transform_style = transform