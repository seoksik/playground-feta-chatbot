# Streamlit
# Use QARetrieval to find informations about the Octo Confluence
# Basic example with a improvementd:
# Add streaming
# Add Conversation history
# Optimize Splitter, Retriever,
# Try Open source models
import streamlit as st
import os
import time
import uuid
from help_desk import HelpDesk
from streamlit_extras.stylable_container import stylable_container
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 페이지 설정
st.set_page_config(
    page_title="Bemily Chatbot",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="auto"
)

# CSS 스타일 추가
st.markdown("""
<style>
    .chat-message {
        padding: 1.5rem; 
        border-radius: 0.5rem; 
        margin-bottom: 1rem;
        display: flex;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .chat-message.user {
        background-color: #e6f3ff;
        border-left: 5px solid #2b6cb0;
    }
    .chat-message.assistant {
        background-color: #f0f4f8;
        border-left: 5px solid #38a169;
    }
    .chat-message .avatar {
        width: 20%;
    }
    .chat-message .content {
        width: 80%;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    div[data-testid="stSidebarNav"] {
        background-image: linear-gradient(to bottom, #4c83b6, #1e3a5f);
        color: white;
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_model():
    """모델 로드 (캐싱)"""
    try:
        with st.spinner("모델을 로드하는 중..."):
            logger.info("HelpDesk 모델 초기화 중...")
            model = HelpDesk(new_db=True, verbose=True)
            logger.info("HelpDesk 모델 초기화 완료")
            return model
    except Exception as e:
        logger.error(f"모델 로드 중 오류 발생: {e}")
        st.error(f"모델 로드 중 오류가 발생했습니다: {str(e)}")
        return None

# 사이드바 추가
with st.sidebar:
    st.title("📚 FETA 이용안내 챗봇")
    st.markdown("---")
    st.markdown("""
    ### 이 챗봇 소개
    
    FETA Gitbook 지식 베이스에 연결된 챗봇 시스템입니다.
    
    **기능:**
    - FETA Gitbook 문서 검색
    - 관련 소스 링크 제공
    - 정확한 답변 생성
    
    ### 사용 방법
    아래 입력창에 질문을 입력하세요. 챗봇이 관련 문서를 검색하고 답변을 제공합니다.
    """)
    
    st.markdown("---")
    
    # 고급 설정
    with st.expander("고급 설정"):
        new_db = st.checkbox("새 DB 생성", value=False, help="체크하면 다음 세션에서 데이터베이스를 새로 생성합니다")
        
        if st.button("세션 초기화"):
            st.session_state.clear()
            st.experimental_rerun()
    
    st.markdown("---")
    # st.markdown("© 2024 RAG-Confluence-Chatbot")

# 메인 컨텐츠
st.title("🤖 FETA 이용가이드 도우미")

# 모델 로드 (진행 상태 표시)
with st.spinner("준비 중..."):
    model = get_model()
    
    if model is None:
        st.error("모델을 로드할 수 없습니다. 관리자에게 문의하세요.")
        st.stop()

# 채팅 이력 초기화
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "안녕하세요! FETA GitBook기반의 서비스 이용안내 도우미입니다. 질문이 있으시면 언제든지 물어보세요. 무엇을 도와드릴까요?", "id": str(uuid.uuid4())}]

# 메시지 표시 - 고유 ID를 사용하여 각 메시지를 식별
for i, msg in enumerate(st.session_state.messages):
    # 메시지에 ID가 없으면 추가
    if "id" not in msg:
        msg["id"] = str(uuid.uuid4())
    
    with stylable_container(
        key=f"msg_{i}_{msg['id']}",  # 메시지의 고유 ID를 키에 포함
        css_styles="""
        {
            border-radius: 10px;
            margin-bottom: 15px;
            padding: 10px;
        }
        """):
        role_style = "user" if msg["role"] == "user" else "assistant"
        role_icon = "🧑‍💻" if msg["role"] == "user" else "🤖"
        
        st.markdown(f"""
        <div class="chat-message {role_style}">
            <div class="avatar">
                {role_icon}
            </div>
            <div class="content">
                {msg["content"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

# 사용자 입력 처리
if prompt := st.chat_input("질문을 입력하세요..."):
    # 사용자 메시지에 고유 ID 추가
    new_msg_id = str(uuid.uuid4())
    st.session_state.messages.append({"role": "user", "content": prompt, "id": new_msg_id})
    
    # 사용자 메시지 표시
    msg_index = len(st.session_state.messages) - 1
    with stylable_container(
        key=f"user_msg_{msg_index}_{new_msg_id}",  # 메시지 인덱스와 고유 ID 모두 사용
        css_styles="""
        {
            border-radius: 10px;
            margin-bottom: 15px;
            padding: 10px;
        }
        """):
        st.markdown(f"""
        <div class="chat-message user">
            <div class="avatar">
                🧑‍💻
            </div>
            <div class="content">
                {prompt}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 응답 생성 표시
    with st.spinner("답변 생성 중..."):
        try:
            logger.info(f"질문 처리 중: {prompt}")
            # 답변 생성
            result, sources = model.retrieval_qa_inference(prompt)
            
            # 응답 메시지에 고유 ID 추가
            assistant_msg_id = str(uuid.uuid4())
            response = f"{result}\n\n{sources}"
            st.session_state.messages.append({"role": "assistant", "content": response, "id": assistant_msg_id})
            
            # 응답 메시지 표시
            msg_index = len(st.session_state.messages) - 1
            with stylable_container(
                key=f"ai_msg_{msg_index}_{assistant_msg_id}",  # 메시지 인덱스와 고유 ID 모두 사용
                css_styles="""
                {
                    border-radius: 10px;
                    margin-bottom: 15px;
                    padding: 10px;
                }
                """):
                st.markdown(f"""
                <div class="chat-message assistant">
                    <div class="avatar">
                        🤖
                    </div>
                    <div class="content">
                        {response}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            logger.info("답변 생성 완료")
            
        except Exception as e:
            logger.error(f"답변 생성 중 오류 발생: {e}")
            st.error(f"죄송합니다. 답변 생성 중 오류가 발생했습니다: {str(e)}")
