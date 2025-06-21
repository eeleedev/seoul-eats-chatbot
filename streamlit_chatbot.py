import os
import logging
import requests
from typing import Dict, List, Optional
import streamlit as st

# LaaS API 키 설정
LAAS_API_KEY = st.secrets["LAAS_API_KEY"]
LAAS_API_URL = "https://api-laas.wanted.co.kr/api/preset/v2/chat/completions"
LAAS_PROJECT = "KNTO-PROMPTON-276"
LAAS_HASH = "c45d97d9d3e8c5027af31035f44b717e546bd1738e77478ac89f1f1e6decf9fb"

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_MESSAGES = 100


def make_laas_api_request(messages: List[Dict]) -> Optional[str]:
    """LaaS API에 요청을 보내고 응답을 받습니다."""
    try:
        response = requests.post(
            LAAS_API_URL,
            headers={"project": LAAS_PROJECT, "apikey": LAAS_API_KEY},
            json={"hash": LAAS_HASH, "params": {}, "messages": messages},
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except requests.RequestException as e:
        logger.error(f"API 요청 중 오류 발생: {str(e)}")
        st.error(f"챗봇 응답을 받는 데 실패했습니다: {str(e)}")
        return None


def add_message(messages: List[Dict[str, str]], role: str, content: str):
    """메시지를 추가하고, 필요한 경우 가장 오래된 메시지를 삭제합니다."""
    messages.append({"role": role, "content": content})
    if len(messages) > MAX_MESSAGES:
        messages.pop(0)


def main():
    st.set_page_config(page_title="🍲 SeoulEats: Your AI Food Guide", page_icon="🍲")
    st.title("🍲 Based on the weather and your cravings, I'll recommend the best Korean food in Seoul!")

    # 세션 상태 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 대화 기록 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 입력
    user_input = st.chat_input("Ask about food, weather, or places in Seoul...")

    if user_input:
        # 사용자 메시지 추가
        add_message(st.session_state.messages, "user", user_input)
        with st.chat_message("user"):
            st.markdown(user_input)

        # 챗봇 응답
        with st.chat_message("assistant"):
            container = st.empty()
            with st.spinner("SeoulEats is typing..."):
                response = make_laas_api_request(st.session_state.messages)
                if response:
                    container.markdown(response)
                    # 챗봇 응답 저장
                    add_message(st.session_state.messages, "assistant", response)
                else:
                    st.error("Failed to get a response.")


if __name__ == "__main__":
    main()