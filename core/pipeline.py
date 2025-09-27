def process_text(input_text, target_language, style):
    """텍스트(또는 이미지 경로)를 받아 번역/스타일 변환/학습 정보를 생성하는 메인 파이프라인.
    1) 입력이 이미지 파일이면 OCR 수행
    2) 번역
    3) 스타일 변환
    4) 학습(변경 단어) 정보 생성
    """
    # 1단계: 입력이 이미지 파일인지 확인 후 OCR 수행
    if isinstance(input_text, str) and input_text.endswith(('.png', '.jpg', '.jpeg')):
        text = ocr_service.extract_text(input_text)
    else:
        text = input_text

    # 2단계: 번역 수행
    translated_text = translation_service.translate(text, target_language)

    # 3단계: 스타일 변환 수행
    styled_text = style_service.transform(translated_text, style)

    # 4단계: 학습 정보(변경 단어 목록 등) 생성
    learning_info = generate_learning_info(text, styled_text)

    return {
        'translated_text': translated_text,
        'styled_text': styled_text,
        'learning_info': learning_info
    }

def generate_learning_info(original_text, styled_text):
    """원본과 스타일 변환 결과를 비교하여 변경된 단어 목록과 의미/예문 정보를 생성."""
    changed_words = text_diff.get_changed_words(original_text, styled_text)
    learning_info = []

    for word in changed_words:
        meaning = get_word_meaning(word)
        example = get_word_example(word)
        learning_info.append({
            'word': word,
            'meaning': meaning,
            'example': example
        })

    return learning_info

def get_word_meaning(word):
    # TODO: 단어 의미 조회 (현재 플레이스홀더)
    return "단어 의미: " + word

def get_word_example(word):
    # TODO: 단어 예문 조회 (현재 플레이스홀더)
    return "예문: " + word

# 파이프라인에서 사용하는 서비스 모듈 임포트
import services.ocr as ocr_service
import services.translation as translation_service
import services.style as style_service
import utils.text_diff as text_diff