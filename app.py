import streamlit as st
st.set_page_config(page_title="Ko-Connect", layout="wide")

import os
from dotenv import load_dotenv
from datetime import datetime

from services.translation import translate_any  # 양방향 번역
from services.style import transform  # 한국어 스타일 변환
from services.ocr import extract_text_from_image  # OCR

load_dotenv()

with open("style.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# --- Streamlit 앱 UI 구성 ---

if not os.getenv("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다. .env 파일 또는 시스템 환경 변수로 키를 설정하세요.")
    st.stop()

# -------------------- 전역 상수/매핑 --------------------
LANG_MAP = {"한국어": "Korean", "영어": "English", "베트남어": "Vietnamese", "중국어": "Chinese"}
STYLE_MAP = {"문어체": "Formal", "구어체": "Informal", "쉬운문장": "Basic Vocabulary", "한자어": "Hanja"}

# -------------------- 세션 초기화 --------------------
if "page" not in st.session_state:
    st.session_state.page = "홈"
if "history" not in st.session_state:
    st.session_state.history = []  # 각 항목: dict(timestamp, source_lang, target_lang, input, output, style(optional))

def render_sidebar_menu():
    """사이드바 메뉴 렌더링 함수."""
    with st.sidebar:
        st.markdown("### 🌐 Ko-Connect")
        selection = st.radio(
            "페이지 이동",
            ("홈", "번역", "기록"),
            index=(0 if st.session_state.page not in ("홈","번역","기록") else ["홈","번역","기록"].index(st.session_state.page))
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
        output_text = transform(translation, STYLE_MAP[style_label])
    # 히스토리 저장
    st.session_state.history.insert(0, {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source_lang": src_label,
        "target_lang": tgt_label,
        "input": input_text,
        "output": output_text,
        "style": applied_style,
    })
    return output_text

# -------------------- 홈 페이지 --------------------
if st.session_state.page == "홈":
    st.title("다국어 번역 & 한국어 문체 변환")
    st.subheader("설명")
    st.write(
        """이 애플리케이션은 한국어와 영어/베트남어/중국어 간 번역 및 
        한국어 결과에 대한 문체(문어체/구어체/쉬운문장/한자어) 변환을 지원합니다. 
        좌측 사이드바에서 '번역' 페이지로 이동하여 텍스트 또는 이미지를 처리하고,
        생성된 결과는 자동으로 '기록' 페이지에 저장됩니다."""
    )
    st.markdown("### 빠른 시작")
    st.markdown("1. 사이드바에서 '번역' 선택 → 2. 입력 언어/타깃 언어 선택 → 3. 텍스트 입력 또는 이미지 업로드 → 4. 실행")
    st.markdown("---")
    st.markdown("#### 현재 저장된 결과 수: {}".format(len(st.session_state.history)))

# -------------------- 번역 페이지 --------------------
elif st.session_state.page == "번역":
    st.title("번역 / 문체 변환")
    input_mode = st.radio("입력 유형 선택", ("텍스트", "이미지"), horizontal=True)

    if input_mode == "텍스트":
        col1, col2 = st.columns(2)
        with col1:
            src_label = st.selectbox("입력 언어", list(LANG_MAP.keys()), index=0)
        with col2:
            tgt_label = st.selectbox("타깃 언어", list(LANG_MAP.keys()), index=1)
        text_input = st.text_area("번역 또는 문체 변환할 텍스트 입력")
        style_label = None
        if tgt_label == "한국어":
            style_label = st.selectbox("한국어 문체 선택", list(STYLE_MAP.keys()))

        if st.button("실행", type="primary"):
            if not text_input.strip():
                st.warning("텍스트를 입력하세요.")
            else:
                try:
                    result = _do_translation(text_input.strip(), src_label, tgt_label, style_label)
                    st.success("완료")
                    st.subheader("결과")
                    st.write(result)
                    st.download_button("결과 다운로드", result, file_name="translation.txt")
                except ValueError as e:
                    st.error(f"오류: {e}")

    else:  # 이미지
        uploaded = st.file_uploader("이미지 업로드", type=["jpg", "jpeg", "png"])
        if uploaded is not None:
            col1, col2 = st.columns(2)
            with col1:
                src_label = st.selectbox("입력 언어", list(LANG_MAP.keys()), index=0, key="img_src")
            with col2:
                tgt_label = st.selectbox("타깃 언어", list(LANG_MAP.keys()), index=1, key="img_tgt")
            style_label = None
            if tgt_label == "한국어":
                style_label = st.selectbox("한국어 문체 선택", list(STYLE_MAP.keys()), key="img_style")
            if st.button("실행", type="primary"):
                extracted = extract_text_from_image(uploaded)
                if not extracted:
                    st.warning("이미지에서 텍스트를 추출하지 못했습니다.")
                else:
                    try:
                        result = _do_translation(extracted, src_label, tgt_label, style_label)
                        st.success("완료")
                        st.subheader("결과")
                        st.write(result)
                        st.download_button("결과 다운로드", result, file_name="translation.txt")
                    except ValueError as e:
                        st.error(f"오류: {e}")
        else:
            st.info("이미지를 업로드하세요.")

# -------------------- 기록 페이지 --------------------
elif st.session_state.page == "기록":
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
            with st.expander(f"[{idx+1}] {item['timestamp']} | {item['source_lang']} → {item['target_lang']}" + (f" | 스타일:{item['style']}" if item['style'] else "")):
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
                        st.session_state.page = "번역"
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
if st.session_state.get('page') == '번역' and 'prefill_text' in st.session_state:
    # 프리필 텍스트를 페이지 상단 안내로 출력 (사용자가 다시 입력하도록 유도)
    with st.expander("이전 기록에서 불러온 텍스트"):
        st.code(st.session_state.prefill_text)
    # 필요시 자동 입력 적용 로직 추가 가능