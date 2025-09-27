import streamlit as st
st.set_page_config(page_title="Konnect", layout="wide")

import os
from dotenv import load_dotenv
from datetime import datetime

from services.translation import translate_any  # 양방향 번역
from services.style import transform  # 한국어 스타일 변환
from services.ocr import extract_text_from_image  # OCR
from services.llm import chat  # llm

load_dotenv()

with open("style.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# --- Streamlit 앱 UI 구성 ---

if not os.getenv("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다. .env 파일 또는 시스템 환경 변수로 키를 설정하세요.")
    st.stop()

# -------------------- 전역 상수/매핑 --------------------
LANG_MAP = {"한국어": "Korean", "영어": "English", "일본어": "Japanese", "중국어": "Chinese", "베트남어": "Vietnamese"}
STYLE_MAP = {
    "문어체": {
        "label": "Formal",
        "desc": "격식을 갖춘 공식 문장체. 논문·보고서 등에 적합"
    },
    "구어체": {
        "label": "Informal",
        "desc": "일상 대화체. 블로그·채팅 등에 자연스러운 문장"
    },
    "쉬운문장": {
        "label": "Basic_Vocabulary",
        "desc": "어린이·외국인도 이해하기 쉬운 기본 단어 위주"
    },
    "한자어": {
        "label": "Hanja",
        "desc": "한자 기반 어휘를 많이 사용하는 문장"
    },
    "서술체": {
        "label": "Narrative",
        "desc": "서술형 문장. 사건이나 이야기등을 서술할 때 적합"
    },
    "묘사체": {
        "label": "Descriptive",
        "desc": "묘사형 문장. 대상이나 장면을 상세하게 묘사할 때 적합"
    }
}

# -------------------- 학습(LLM 분석) 프롬프트 템플릿 --------------------
# ROLE / INPUT / GUIDELINES / OUTPUT FORMAT 구조 유지. service.llm.chat 에서는 messages 배열로 전달.
LEARNING_PROMPTS = {
    "diff": (
        """[ROLE]\n한국어 문장 교정 차이 분석 전문가.\n\n"
        "[INPUT]\n원문: {original}\n수정문: {revised}\n\n"
        "[GUIDELINES]\n"
        "1) 의미 변화, 어휘 교체, 문형/종결어미/시제/높임 변화만 핵심 bullet 로 요약.\n"
        "2) 수정되지 않은 부분 설명 금지.\n"
        "3) 추측/과장/평가 금지.\n"
        "4) 5줄 이내.\n\n"
        "[OUTPUT FORMAT]\n- 항목1\n- 항목2 ... (불필요한 머리말/맺음말 금지)"""
    ),
    "meaning": (
        """[ROLE]\n한국어 어휘/문법 학습 설명가. 교정 전후 차이를 학습자 관점에서 설명.\n\n"
        "[INPUT]\n원문: {original}\n수정문: {revised}\n\n"
        "[GUIDELINES]\n"
        "1) 바뀐 어휘/표현만 다룬다 (변경되지 않은 단어 배제).\n"
        "2) 각 항목: (변경된표현) -> 의미 / 쓰임 / 문법 포인트 / 유의어(최대2).\n"
        "3) 과도한 학술 용어, 한자 괄호 표기 자제.\n"
        "4) 문장 재작성/추가 번역 금지.\n"
        "5) 8항목 이내.\n\n"
        "[OUTPUT FORMAT]\n(표현1) : 의미 / 문법 / 유의어\n(표현2) : ..."""
    ),
    "examples": (
        """[ROLE]\n한국어 예문 생성 튜터. 수정된 문장의 핵심 변경 표현을 반복·강화하는 학습 예문 작성.\n\n"
        "[INPUT]\n수정문: {revised}\n\n"
        "[GUIDELINES]\n"
        "1) 3개의 짧고 자연스러운 예문.\n"
        "2) 각 예문은 서로 다른 맥락.\n"
        "3) 어려운 고급어/불필요한 한자어 피함.\n"
        "4) 동일 핵심 표현 재사용 가능 (학습 강화 목적).\n"
        "5) 번호 매기기.\n\n"
        "[OUTPUT FORMAT]\n1) 예문\n2) 예문\n3) 예문"""
    ),
}

# -------------------- 세션 초기화 --------------------
if "page" not in st.session_state:
    st.session_state.page = "홈"
if "history" not in st.session_state:
    st.session_state.history = []  # 각 항목: dict(timestamp, source_lang, target_lang, input, output, style(optional))

def render_sidebar_menu():
    """사이드바 메뉴 렌더링 함수."""
    with st.sidebar:
        st.markdown("### 🌐 Konnect")
        selection = st.radio(
            "페이지 이동",
            ("🏠홈", "🔎번역", "📄기록", "📝학습"),
            index=(0 if st.session_state.page not in ("🏠홈","🔎번역","📄기록","📝학습") else ["🏠홈","🔎번역","📄기록","📝학습"].index(st.session_state.page))
        )
        st.markdown("---")
        st.caption("페이지 이동 시 결과는 세션에 저장됩니다.")
    st.session_state.page = selection

# 사이드바 렌더 함수 호출
render_sidebar_menu()

# -------------------- 공통 함수 --------------------
def _do_translation(input_text: str, src_label: str, tgt_label: str, style_label: str | None):
    src = LANG_MAP[src_label]
    tgt = LANG_MAP[tgt_label]
    translation = translate_any(input_text, src, tgt)
    output_text = translation
    applied_style = None
    if tgt == "Korean" and style_label:
        applied_style = style_label
        # transform에는 영어 라벨 문자열을 전달하도록 통일
        output_text = transform(translation, STYLE_MAP[style_label]["label"])
    # 히스토리 저장
    st.session_state.history.insert(0, {
        "timestamp": datetime.now().strftime("%Y-%m-%d"),
        "source_lang": src_label,
        "target_lang": tgt_label,
        "input": input_text,
        "output": output_text,
        "style": applied_style,
    })
    return output_text

# -------------------- 홈 페이지 --------------------
if st.session_state.page == "🏠홈":
    st.title("Konnect")
    st.markdown("#### 한국어 학습을 위한 스마트 번역 & 학습 도구")
    # 홈페이지 타이틀 아래: 우선 images 폴더의 특정 이미지를 먼저 표시하고 충분한 간격을 둔 뒤 다른 이미지를 표시
    first_img = "images/translate-translation-vector-logo-design-template_1141934-3723.jpg"

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image(first_img, use_container_width=True)

    st.markdown("---")
    st.header("다국어 번역 & 한국어 문체 변환")
    st.markdown(
        f"""### 개요
학습자 친화적인 한↔다국어 번역과 한국어 문체(스타일) 재작성 기능을 통합 제공하는 도구입니다. 결과는 자동으로 기록되어 재사용·학습 분석에 활용할 수 있습니다.

### 지원 언어
- 한국어 ↔ **영어 / 일본어 / 중국어(간체) / 베트남어**

### 번역 품질 원칙
- 의미/뉘앙스 보존, 과도한 의역·설명 제거
- 고유명사·형식 유지 / 줄바꿈 구조 반영
- 학습·교육 맥락에 자연스러운 문장 지향

### 한국어 문체 변환
| 문체 | 특징 |
| ---- | ----- |
| 문어체 | 격식 있고 정제된 공식체 (보고서/논문) |
| 구어체 | 자연스러운 일상 대화체 (블로그/채팅) |
| 쉬운문장 | 초급 학습자도 쉽게 읽는 기본 어휘 중심 |
| 한자어 | 적절한 한자어 활용으로 격식·전문성 강화 |
| 서술체 | 사건 전개 중심, 시간/흐름 명확 |
| 묘사체 | 감각·형용 표현 강화로 장면 묘사 강조 |

### 이미지 OCR
- 이미지 업로드 → 텍스트 추출 → 번역/문체 변환 가능
- 현재 기본 추출 로직

### 학습 도구 (📝학습 페이지)
- 교정 전/후 차이 요약 (형태·어미·어휘 변화)
- 변화된 표현 의미/문법/유의어 정리
- 학습용 예문 3개 자동 생성

### 기록 & 재사용
- 모든 결과 자동 저장 / 필터링 / 삭제 / txt 다운로드
- 기록 항목을 다시 불러와 편집·추가 변환 가능

### 빠른 시작
1. 사이드바에서 **🔎번역** 선택
2. 입력 언어 / 타깃 언어 / (한국어 타깃 시) 문체 고르기
3. 텍스트 입력 또는 이미지 업로드
4. 실행 → 결과 확인 후 필요 시 **📄기록** / **📝학습** 활용

"""
    )
# -------------------- 번역 페이지 --------------------
elif st.session_state.page == "🔎번역":
    st.title("번역 및 문체 변환")
    tab_text, tab_image = st.tabs(["텍스트 입력", "이미지 업로드"])

    # --- 텍스트 탭 ---
    with tab_text:
        col1, col2 = st.columns(2)
        with col1:
            src_label = st.selectbox("입력 언어", list(LANG_MAP.keys()), index=0, key="text_src")
        with col2:
            tgt_label = st.selectbox("타깃 언어", list(LANG_MAP.keys()), index=1, key="text_tgt")
        text_input = st.text_area("번역 또는 문체 변환할 텍스트 입력", key="text_input_area")
        style_label = None
        if tgt_label == "한국어":
            style_label = st.selectbox(
                "한국어 문체 선택",
                list(STYLE_MAP.keys()),
                format_func=lambda k: f"{k} ： {STYLE_MAP[k]['desc']}",
                key="text_style"
            )
        if st.button("텍스트 실행", type="primary", key="run_text"):
            if not text_input.strip():
                st.warning("텍스트를 입력하세요.")
            else:
                try:
                    result = _do_translation(text_input.strip(), src_label, tgt_label, style_label)
                    st.success("완료")
                    st.subheader("결과")
                    st.write(result)
                    st.download_button("결과 다운로드", result, file_name="translation.txt", key="dl_text_result")
                except ValueError as e:
                    st.error(f"오류: {e}")

    # --- 이미지 탭 ---
    with tab_image:
        uploaded = st.file_uploader("이미지 업로드", type=["jpg", "jpeg", "png"], key="img_uploader")
        if uploaded is not None:
            col1, col2 = st.columns(2)
            with col1:
                src_label_img = st.selectbox("입력 언어", list(LANG_MAP.keys()), index=0, key="img_src")
            with col2:
                tgt_label_img = st.selectbox("타깃 언어", list(LANG_MAP.keys()), index=1, key="img_tgt")
            style_label_img = None
            if tgt_label_img == "한국어":
                style_label_img = st.selectbox("한국어 문체 선택", list(STYLE_MAP.keys()), key="img_style")
            if st.button("이미지 실행", type="primary", key="run_image"):
                extracted = extract_text_from_image(uploaded)
                if not extracted:
                    st.warning("이미지에서 텍스트를 추출하지 못했습니다.")
                else:
                    try:
                        result = _do_translation(extracted, src_label_img, tgt_label_img, style_label_img)
                        st.success("완료")
                        st.subheader("결과")
                        st.write(result)
                        st.download_button("결과 다운로드", result, file_name="translation.txt", key="dl_image_result")
                    except ValueError as e:
                        st.error(f"오류: {e}")
        else:
            st.info("이미지를 업로드하세요.")

# -------------------- 기록 페이지 --------------------
elif st.session_state.page == "📄기록":
    st.title("저장된 번역 기록")
    if not st.session_state.history:
        st.info("아직 저장된 기록이 없습니다. '번역' 페이지에서 새 결과를 생성하세요.")
    else:
        # 필터
        with st.expander("필터 / 정렬", expanded=False):
            lang_filter = st.multiselect("타깃 언어 필터", options=list(LANG_MAP.keys()))
            style_filter = st.multiselect("스타일 필터", options=list(STYLE_MAP.keys()))
        filtered = st.session_state.history
        if lang_filter:
            filtered = [h for h in filtered if h["target_lang"] in lang_filter]
        if style_filter:
            filtered = [h for h in filtered if (h["style"] in style_filter)]

        for idx, item in enumerate(filtered):
            with st.expander(f"[{item['timestamp']}] : {item['input'][:5]} | {item['source_lang']} → {item['target_lang']}" + (f" | 스타일:{item['style']}" if item['style'] else "")):
                st.markdown("**입력**")
                st.write(item['input'])
                st.markdown("**출력**")
                st.write(item['output'])
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.download_button("출력 저장", item['output'], file_name=f"translation_{idx+1}.txt", key=f"dl_{idx}")
                with col_b:
                    if st.button("재사용(편집창으로 보내기)", key=f"reuse_{idx}"):
                        # 재사용 시 번역 페이지로 이동 & 입력 프리필
                        st.session_state.page = "🔎번역"
                        st.session_state.prefill_text = item['input']
                        st.rerun()
                with col_c:
                    if st.button("삭제", key=f"del_{idx}"):
                        st.session_state.history.remove(item)
                        st.rerun()

    # 전체 삭제
    if st.session_state.history:
        if st.button("전체 기록 초기화", type="secondary"):
            st.session_state.history.clear()
            st.rerun()

# -------------------- 번역 페이지 프리필 처리 (재사용 기능) --------------------
if st.session_state.get('page') == '🔎번역' and 'prefill_text' in st.session_state:
    # 프리필 텍스트를 페이지 상단 안내로 출력 (사용자가 다시 입력하도록 유도)
    with st.expander("이전 기록에서 불러온 텍스트"):
        st.code(st.session_state.prefill_text)
    # 필요시 자동 입력 적용 로직 추가 가능

# -------------------- 학습 페이지 --------------------
elif st.session_state.page == "📝학습":
    st.title("수정 단어 & 예문 학습")
    if not st.session_state.history:
        st.info("저장된 번역 기록이 없습니다.")
    else:
        # 옵션 문자열 구성 (타임스탬프는 날짜만 존재하므로 잘려도 안전)
        options = [
            f"[{i+1:02}]  {h['timestamp'][:16]}  "
            f"({h['source_lang']}→{h['target_lang']})" + (f"  –  {h['style']}" if h['style'] else "")
            for i, h in enumerate(st.session_state.history)
        ]
        choice = st.selectbox("기록 선택", options)
        idx = options.index(choice)
        record = st.session_state.history[idx]

        # 선택한 기록 표시
        st.markdown("### 선택한 기록")
        st.markdown("**입력**")
        st.write(record['input'])
        st.markdown("**출력**")
        st.write(record['output'])
        st.markdown("---")

        # 결과 저장용 세션 키 초기화
        if 'learning_results' not in st.session_state:
            st.session_state.learning_results = {"diff": "", "meaning": "", "example": ""}

        if record["source_lang"] == "한국어" and record["target_lang"] == "한국어":
            st.markdown("### LLM 학습 도구")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("차이점 확인"):
                    with st.spinner("차이점 분석 중..."):
                        prompt = LEARNING_PROMPTS["diff"].format(original=record['input'], revised=record['output'])
                        st.session_state.learning_results["diff"] = chat([
                            {"role": "system", "content": "주어진 지침을 엄격히 따르는 한국어 문장 차이 분석기"},
                            {"role": "user", "content": prompt}
                        ])
            with col2:
                if st.button("수정 단어 의미/구조"):
                    with st.spinner("의미/구조 설명 생성 중..."):
                        prompt = LEARNING_PROMPTS["meaning"].format(original=record['input'], revised=record['output'])
                        st.session_state.learning_results["meaning"] = chat([
                            {"role": "system", "content": "지침 기반 한국어 표현 변화 의미·문법 설명기"},
                            {"role": "user", "content": prompt}
                        ])
            with col3:
                if st.button("공부 예문 생성"):
                    with st.spinner("예문 생성 중..."):
                        prompt = LEARNING_PROMPTS["examples"].format(revised=record['output'])
                        st.session_state.learning_results["example"] = chat([
                            {"role": "system", "content": "지침을 따르는 한국어 학습 예문 생성기"},
                            {"role": "user", "content": prompt}
                        ])

            # 버튼 결과 출력
            if st.session_state.learning_results["diff"]:
                st.subheader("차이점")
                st.write(st.session_state.learning_results["diff"])
            if st.session_state.learning_results["meaning"]:
                st.subheader("수정 단어 의미/구조")
                st.write(st.session_state.learning_results["meaning"])
            if st.session_state.learning_results["example"]:
                st.subheader("공부 예문")
                st.write(st.session_state.learning_results["example"])