import sys
import logging
import collections
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage

import load_db

class HelpDesk():
    """Create the necessary objects to create a QARetrieval chain"""
    def __init__(self, new_db=True, verbose=False):
        # 로깅 설정
        self.logger = logging.getLogger(__name__)
        if not self.logger.hasHandlers():
            logging.basicConfig(level=logging.INFO if verbose else logging.WARNING, 
                               format='%(asctime)s - %(levelname)s - %(message)s')
        
        self.logger.info("HelpDesk 초기화 시작...")
        self.new_db = new_db
        self.template = self.get_template()
        self.embeddings = self.get_embeddings()
        self.llm = self.get_llm()
        self.prompt = self.get_prompt()

        try:
            if self.new_db:
                self.logger.info("새 DB를 생성합니다...")
                self.db = load_db.DataLoader().set_db(self.embeddings)
            else:
                self.logger.info("기존 DB를 로드합니다...")
                self.db = load_db.DataLoader().get_db(self.embeddings)
                
            self.retriever = self.db.as_retriever(search_kwargs={"k": 4})  # 더 많은 문서 검색
            self.retrieval_qa_chain = self.get_retrieval_qa()
            self.logger.info("HelpDesk 초기화 완료")
        except Exception as e:
            self.logger.error(f"HelpDesk 초기화 중 오류 발생: {e}")
            raise

    def get_template(self):
        template = """
        주어진 텍스트 조각을 기반으로 질문에 답변해 주세요:
        -----
        {context}
        -----
        
        위 내용을 바탕으로 다음 질문에 친절하고 정확하게 답변해 주세요:
        질문: {question}
        
        맥락에 해당하는 정보가 없다면 "모르겠습니다"라고 답변하세요.
        """
        return template

    def get_prompt(self) -> PromptTemplate:
        prompt = PromptTemplate(
            template=self.template,
            input_variables=["context", "question"]
        )
        return prompt

    def get_embeddings(self) -> OpenAIEmbeddings:
        """OpenAI 임베딩 객체 생성"""
        try:
            self.logger.info("OpenAI 임베딩 초기화 중...")
            # 모델명 지정 및 차원 크기 설정으로 최적화
            embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",  # 더 효율적인 임베딩 모델
                dimensions=1024,  # 임베딩 차원 지정
                retry_min_seconds=1,
                retry_max_seconds=60,
                show_progress_bar=True
            )
            self.logger.info("임베딩 초기화 완료")
            return embeddings
        except Exception as e:
            self.logger.error(f"임베딩 초기화 중 오류 발생: {e}")
            raise

    def get_llm(self):
        """OpenAI LLM 객체 생성"""
        try:
            self.logger.info("OpenAI LLM 초기화 중...")
            # OpenAI 대신 ChatOpenAI 사용 (더 성능이 좋음)
            llm = ChatOpenAI(
                model_name="gpt-3.5-turbo",  # 비용 효율적인 모델 사용
                temperature=0,  # 결정적 출력
                streaming=True  # 스트리밍 지원 (더 나은 UX)
            )
            self.logger.info("LLM 초기화 완료")
            return llm
        except Exception as e:
            self.logger.error(f"LLM 초기화 중 오류 발생: {e}")
            raise

    def get_retrieval_qa(self):
        """RetrievalQA 체인 생성"""
        try:
            self.logger.info("RetrievalQA 체인 생성 중...")
            chain_type_kwargs = {"prompt": self.prompt}
            qa = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.retriever,
                return_source_documents=True,
                chain_type_kwargs=chain_type_kwargs,
                verbose=False
            )
            self.logger.info("RetrievalQA 체인 생성 완료")
            return qa
        except Exception as e:
            self.logger.error(f"RetrievalQA 체인 생성 중 오류 발생: {e}")
            raise

    def retrieval_qa_inference(self, question, verbose=True):
        """주어진 질문에 대한 답변 및 소스 문서 반환"""
        try:
            self.logger.info(f"질문에 대한 추론 시작: '{question[:50]}...'")
            # __call__ 대신 invoke 메서드 사용
            answer = self.retrieval_qa_chain.invoke({"query": question})
            sources = self.list_top_k_sources(answer, k=2)
            
            if verbose:
                print(sources)
                
            self.logger.info("추론 완료")
            return answer["result"], sources
        except Exception as e:
            self.logger.error(f"추론 중 오류 발생: {e}")
            error_msg = "죄송합니다. 질문 처리 중 오류가 발생했습니다."
            return error_msg, "오류가 발생했습니다. 잠시 후 다시 시도해 주세요."

    def list_top_k_sources(self, answer, k=2):
        """소스 문서 목록 반환"""
        try:
            sources = []
            if "source_documents" in answer and answer["source_documents"]:
                sources = [
                    f'[{res.metadata.get("title", "제목 없음")}]({res.metadata.get("source", "#")})'
                    for res in answer["source_documents"]
                    if hasattr(res, "metadata")
                ]
            
            if not sources:
                return "소스 문서를 찾을 수 없습니다."
            
            k = min(k, len(sources))
            counter = collections.Counter(sources)
            most_common = counter.most_common(k)
            
            if not most_common:
                return "소스 문서를 찾을 수 없습니다."
                
            distinct_sources = [source for source, _ in most_common]
            distinct_sources_str = "  \n- ".join(distinct_sources)
            
            if len(distinct_sources) == 1:
                return f"여기에 도움이 될 수 있는 자료가 있어요:  \n- {distinct_sources_str}"
            elif len(distinct_sources) > 1:
                return f"여기에 도움이 될 수 있는 자료 {len(distinct_sources)}개가 있어요:  \n- {distinct_sources_str}"
            else:
                return "미안하지만, 질문에 답할 자료를 찾지 못했어요."
        except Exception as e:
            self.logger.error(f"소스 문서 처리 중 오류 발생: {e}")
            return "소스 문서 정보를 처리하는 중 오류가 발생했습니다."