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
    "Formal": "다음 문장을 문어체(격식체)로 다시 작성하세요: {text}"
                "격식을 갖춘 공식 문장체. 논문·보고서 등에 적합",
    "Informal": "다음 문장을 구어체(친근한 말투)로 다시 작성하세요: {text}"
                "일상 대화체. 블로그·채팅 등에 자연스러운 문장",
    "Basic_Vocabulary": "다음 문장을 더 쉬운 기초 단어 위주로 다시 작성하세요: {text}"
                "어린이·외국인도 이해하기 쉬운 기본 단어 위주",
    "Hanja": "다음 문장에서 사용할 수 있는 한자어를 적극 사용하여 다시 작성하세요: {text}"
                "한자 기반 어휘를 많이 사용하는 문장",
    "Narrative": "다음 문장을 서술체로 다시 작성하세요: {text}"
                "서술형 문장. 사건이나 이야기등을 서술할 때 적합",
    "Descriptive": "다음 문장을 묘사체로 다시 작성하세요: {text}"
                "묘사형 문장. 대상이나 장면을 상세하게 묘사할 때 적합",
}

ocr_prompt = "다음 이미지에서 한국어 텍스트를 추출하세요: {image_url}"