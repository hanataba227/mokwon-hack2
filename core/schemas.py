from pydantic import BaseModel
from typing import List, Optional

# 데이터 교환을 위한 Pydantic 스키마 정의

class TranslationRequest(BaseModel):
    source_text: str  # 원본 텍스트
    target_language: str  # 목표 언어

class TranslationResponse(BaseModel):
    translated_text: str  # 번역 결과
    source_language: str  # 감지된 원본 언어
    target_language: str  # 목표 언어

class StyleTransformationRequest(BaseModel):
    text: str  # 변환 대상 텍스트
    style: str  # 스타일 종류

class StyleTransformationResponse(BaseModel):
    transformed_text: str  # 변환된 결과 텍스트
    changed_words: List[str]  # 변경된 단어 목록

class OCRRequest(BaseModel):
    image_path: str  # 이미지 경로

class OCRResponse(BaseModel):
    extracted_text: str  # 추출된 텍스트

class LearningAssistResponse(BaseModel):
    changed_words: List[str]  # 변경된 단어
    meanings: List[str]  # 의미 목록
    examples: List[str]  # 예문 목록