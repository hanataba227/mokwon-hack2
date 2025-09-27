# 번역, 스타일 변환, OCR 처리를 위한 프롬프트 템플릿 모음

translation_prompts = {
    "korean_to_english": "다음 한국어 문장을 영어로 번역하세요: {text}",
    "english_to_korean": "다음 영어 문장을 한국어로 번역하세요: {text}",
    "korean_to_vietnamese": "다음 한국어 문장을 베트남어로 번역하세요: {text}",
    "vietnamese_to_korean": "다음 베트남어 문장을 한국어로 번역하세요: {text}",
    "korean_to_chinese": "다음 한국어 문장을 중국어(간체)로 번역하세요: {text}",
    "chinese_to_korean": "다음 중국어 문장을 한국어로 번역하세요: {text}",
}

style_transformation_prompts = {
    "formal": "다음 문장을 문어체(격식체)로 다시 작성하세요: {text}",
    "informal": "다음 문장을 구어체(친근한 말투)로 다시 작성하세요: {text}",
    "basic_vocabulary": "다음 문장을 더 쉬운 기초 단어 위주로 다시 작성하세요: {text}",
    "hanja": "다음 문장에서 사용할 수 있는 한자어를 적극 사용하여 다시 작성하세요: {text}",
}

ocr_prompt = "다음 이미지에서 한국어 텍스트를 추출하세요: {image_url}"