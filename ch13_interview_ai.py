import streamlit as st
from openai import OpenAI

# 세션 상태 선언
if "interview_question" not in st.session_state:
    st.session_state.interview_question = None
if "client" not in st.session_state:
    st.session_state.client = None
if "transcription" not in st.session_state:
    st.session_state.transcription = None

# AI 응답 생성 함수 정의(질문 생성, 답변 분석)
def process_text(prompt: str, client):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

def main():
    st.set_page_config(layout="wide")
    st.title("면접 준비 도우미")
    with st.sidebar:
        openai_api_key = st.text_input(
            "OpenAI API Key",
            type="password",
        )
        st.markdown("[OpenAI API Key 받기](https://platform.openai.com/account/api-keys)")
    default_job_info = """데이터 분석가 직무 정보:
1. 주요 업무
- 데이터 수집 및 정제: 다양한 소스에서 데이터를 수집하고 분석 가능한 형태로 정제
- 데이터 분석: 통계, 머신러닝, 인공지능 기법을 이용해 데이터를 분석하고 패턴을 찾음
- 시각화 및 보고: 분석 결과를 이해하기 쉽게 시각화하고 보고서로 작성해 의사결정자에게 전달
2. 필요 역량
- 기술적 역량: 통계학, 수학, 프로그래밍 언어(R, 파이썬 등), 데이터베이스 관리(SQL 등)
- 문제 해결 능력: 데이터를 통해 비즈니스 문제를 분석하고 해결책 제시
"""
    # 직무 정보 입력 위젯 생성
    user_input = st.text_area(
        "직무 정보를 입력하세요:",
        value=default_job_info,
        height=200,
    )
    if st.button("질문 생성"):
        if not openai_api_key:
            st.info("계속하려면 OpenAI API Key를 추가하세요.")
            st.stop()
        # OpenAI 클라이언트 생성
        st.session_state.client = OpenAI(api_key=openai_api_key)
        # 질문 생성을 위한 프롬프트 작성
        prompt = f"""
        너는 채용 전문 컨설턴트야.
        주어진 직무 정보를 바탕으로 면접 시 예상 질문 하나를 생성해줘.
        - 3분 이내로 답변이 가능한 질문을 생성해.
        - 단순히 질문만 출력해.
        - 직무 정보: {user_input}
        """
        # 질문 생성
        with st.spinner("질문 생성 중..."):
            st.session_state.interview_question = process_text(
                prompt,
                st.session_state.client,
            )
            st.success("질문 생성 완료!")
    # 질문 출력
    if st.session_state.interview_question:
        st.write("### 예상 질문: ")
        st.write(f"{st.session_state.interview_question}")
        st.write("### 답변 녹음 후 평가받기")
    # 답변 녹음 후 저장
    audio = st.audio_input("답변 녹음하기")
    if audio and st.button("답변 평가받기"):
        if not openai_api_key:
            st.info("계속하려면 OpenAI API Key를 추가하세요.")
            st.stop()
        with st.spinner("답변 평가 중..."):
            # 음성-텍스트 변환값 변수명 수정
            st.session_state.transcription = st.session_state.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                response_format="text"
            )
            # 답변 분석을 위한 프롬프트 작성
            evaluation_prompt = f"""
            너는 전문 면접관이야.
            지원자가 다음 질문에 대한 답변을 녹음해 제공했어.
            질문: {st.session_state.interview_question}
            지원자의 답변을 다음 기준으로 평가해줘.
            1. 답변의 논리적 구조
            2. 면접 질문과의 관련성
            3. 개선할 점
            - 마크다운 형식으로 정리해.
            - 장점과 단점을 명확히 구분해서 설명해.
            지원자의 답변: {st.session_state.transcription}
            """
            # 답변 분석
            evaluation = process_text(evaluation_prompt, st.session_state.client)
            # 두 개의 탭 생성 및 결과 출력
            tab1, tab2 = st.tabs(["답변 분석", "답변 원본"])
            with tab1:
                st.write(evaluation)
            with tab2:
                st.write(st.session_state.transcription)

if __name__ == "__main__":
    main()
