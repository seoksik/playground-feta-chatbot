import sys
import logging
import shutil
import os
import tqdm
import requests
import xml.etree.ElementTree as ET
from typing import List, Optional
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# 상대 경로 대신 절대 경로 사용
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import (CONFLUENCE_SPACE_NAME, CONFLUENCE_SPACE_KEY,
                   CONFLUENCE_USERNAME, CONFLUENCE_API_KEY, PERSIST_DIRECTORY,
                   GITBOOK_DOMAIN, GITBOOK_SITEMAP, DOCUMENT_SOURCE)

# 최신 패키지 사용
from langchain_community.document_loaders import ConfluenceLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters import MarkdownHeaderTextSplitter
# Chroma 패키지를 권장 방식으로 변경
from langchain_chroma import Chroma
from langchain_core.documents import Document

class GitBookLoader:
    """GitBook 문서를 로드하는 클래스"""
    
    def __init__(self, sitemap_url):
        self.sitemap_url = sitemap_url
        self.logger = logging.getLogger(__name__)
    
    def get_urls_from_sitemap(self):
        """사이트맵 XML에서 모든 URL을 추출"""
        try:
            self.logger.info(f"사이트맵에서 URL 목록 가져오는 중: {self.sitemap_url}")
            response = requests.get(self.sitemap_url)
            response.raise_for_status()
            
            # XML 파싱
            root = ET.fromstring(response.content)
            
            # XML 네임스페이스 처리
            namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            # URL 추출
            urls = []
            for url in root.findall('.//ns:url/ns:loc', namespaces):
                urls.append(url.text)
            
            self.logger.info(f"사이트맵에서 {len(urls)}개 URL을 찾았습니다.")
            return urls
        
        except Exception as e:
            self.logger.error(f"사이트맵 처리 중 오류 발생: {e}")
            return []
    
    def load(self):
        """모든 GitBook 페이지를 로드하여 Document 객체 리스트로 반환"""
        urls = self.get_urls_from_sitemap()
        
        if not urls:
            self.logger.warning("URL을 찾을 수 없습니다.")
            return []
        
        all_docs = []
        # 배치 크기
        batch_size = 10
        
        for i in tqdm.tqdm(range(0, len(urls), batch_size)):
            batch_urls = urls[i:i+batch_size]
            try:
                # WebBaseLoader를 사용하여 여러 URL을 한 번에 로드
                loader = WebBaseLoader(batch_urls)
                docs = loader.load()
                
                # 메타데이터 보강
                for j, doc in enumerate(docs):
                    url = batch_urls[j]
                    parsed_url = urlparse(url)
                    path_parts = parsed_url.path.strip('/').split('/')
                    
                    # 메타데이터 설정
                    if 'metadata' not in doc.__dict__:
                        doc.metadata = {}
                    
                    doc.metadata.update({
                        'source': url,
                        'title': path_parts[-1].replace('-', ' ').title() if path_parts else 'Untitled',
                        'space_key': 'gitbook',
                        'content_type': 'GitBook Page'
                    })
                
                all_docs.extend(docs)
                self.logger.info(f"배치 {i//batch_size + 1}/{(len(urls)-1)//batch_size + 1} 처리 완료 ({len(docs)}개 문서)")
            
            except Exception as e:
                self.logger.error(f"배치 {i//batch_size + 1} 로드 중 오류 발생: {e}")
        
        self.logger.info(f"총 {len(all_docs)}개 GitBook 문서를 로드했습니다.")
        return all_docs

class DataLoader():
    """Create, load, save the DB using the confluence Loader"""
    def __init__(
        self,
        confluence_url=CONFLUENCE_SPACE_NAME,
        username=CONFLUENCE_USERNAME,
        api_key=CONFLUENCE_API_KEY,
        space_key=CONFLUENCE_SPACE_KEY,
        persist_directory=PERSIST_DIRECTORY,
        gitbook_sitemap=GITBOOK_SITEMAP,
        document_source=DOCUMENT_SOURCE
    ):

        self.confluence_url = confluence_url
        self.username = username
        self.api_key = api_key
        self.space_key = space_key
        self.persist_directory = persist_directory
        self.gitbook_sitemap = gitbook_sitemap
        self.document_source = document_source.lower()
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def load_from_confluence_loader(self):
        """Load HTML files from Confluence"""
        self.logger.info("Confluence에서 문서 로딩 중...")
        loader = ConfluenceLoader(
            url=self.confluence_url,
            username=self.username,
            api_key=self.api_key,
            space_key=self.space_key
        )

        docs = loader.load()
        self.logger.info(f"{len(docs)}개 문서를 Confluence에서 로드했습니다.")
        return docs

    def load_from_gitbook_loader(self):
        """GitBook에서 문서 로드"""
        self.logger.info("GitBook에서 문서 로딩 중...")
        loader = GitBookLoader(sitemap_url=self.gitbook_sitemap)
        docs = loader.load()
        self.logger.info(f"{len(docs)}개 문서를 GitBook에서 로드했습니다.")
        return docs

    def load_documents(self):
        """설정된 문서 소스에 따라 문서 로드"""
        all_docs = []
        
        if self.document_source in ['confluence', 'both']:
            confluence_docs = self.load_from_confluence_loader()
            all_docs.extend(confluence_docs)
            self.logger.info(f"Confluence 문서 {len(confluence_docs)}개 로드 완료")
        
        if self.document_source in ['gitbook', 'both']:
            gitbook_docs = self.load_from_gitbook_loader()
            all_docs.extend(gitbook_docs)
            self.logger.info(f"GitBook 문서 {len(gitbook_docs)}개 로드 완료")
        
        self.logger.info(f"총 {len(all_docs)}개 문서를 로드했습니다.")
        return all_docs

    def split_docs(self, docs):
        """문서를 적절한 크기로 분할하여 처리합니다.
        
        1. 먼저 마크다운 헤더를 기준으로 분할
        2. 그 다음 RecursiveCharacterTextSplitter로 더 작은 청크로 분할
        3. 토큰 수가 너무 많은 문서를 검사하고 추가로 분할
        """
        self.logger.info("문서 분할 시작...")
        
        # 마크다운 헤더 기준으로 분할
        headers_to_split_on = [
            ("#", "Titre 1"),
            ("##", "Sous-titre 1"),
            ("###", "Sous-titre 2"),
        ]

        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

        # Split based on markdown and add original metadata
        md_docs = []
        for doc in docs:
            md_doc = markdown_splitter.split_text(doc.page_content)
            for i in range(len(md_doc)):
                md_doc[i].metadata = md_doc[i].metadata | doc.metadata
            md_docs.extend(md_doc)
        
        self.logger.info(f"마크다운 헤더 분할 후 {len(md_docs)}개 문서로 나뉘었습니다.")

        # 청크 크기를 좀 더 작게 설정 (512 -> 300)하여 토큰 수를 제한
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,  # 청크 크기 축소
            chunk_overlap=20,
            separators=["\n\n", "\n", "(?<=\. )", " ", ""],
            length_function=len  # 단순 문자 길이 기준
        )

        splitted_docs = splitter.split_documents(md_docs)
        self.logger.info(f"문서 분할 완료: 총 {len(splitted_docs)}개 청크 생성")
        
        return splitted_docs

    def save_to_db_batch(self, splitted_docs, embeddings, batch_size=100):
        """문서를 배치로 나누어 임베딩 후 Chroma DB에 저장합니다.
        
        Args:
            splitted_docs: 분할된 문서 리스트
            embeddings: 임베딩 함수
            batch_size: 한 번에 처리할 문서 수
        """
        self.logger.info(f"총 {len(splitted_docs)}개 문서를 {batch_size}개씩 배치로 처리하여 DB 저장 시작...")
        
        # Chroma 컬렉션 생성
        db = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=embeddings
        )
        
        # 배치 처리
        for i in tqdm.tqdm(range(0, len(splitted_docs), batch_size)):
            batch = splitted_docs[i:i+batch_size]
            
            # 배치 내 문서에서 텍스트, 메타데이터 추출
            texts = [doc.page_content for doc in batch]
            metadatas = [doc.metadata for doc in batch]
            
            try:
                # 임베딩 생성 및 추가
                db.add_texts(texts=texts, metadatas=metadatas)
                self.logger.info(f"배치 {i//batch_size + 1}/{(len(splitted_docs)-1)//batch_size + 1} 처리 완료")
            except Exception as e:
                self.logger.error(f"배치 {i//batch_size + 1} 처리 중 오류 발생: {e}")
                # 배치 크기를 절반으로 줄여 재시도
                half_batch_size = batch_size // 2
                if half_batch_size > 0:
                    self.logger.info(f"배치 크기를 {half_batch_size}로 줄여 재시도합니다.")
                    for j in range(i, min(i+batch_size, len(splitted_docs)), half_batch_size):
                        smaller_batch = splitted_docs[j:j+half_batch_size]
                        texts = [doc.page_content for doc in smaller_batch]
                        metadatas = [doc.metadata for doc in smaller_batch]
                        try:
                            db.add_texts(texts=texts, metadatas=metadatas)
                            self.logger.info(f"작은 배치 처리 완료: {j}-{j+len(smaller_batch)}")
                        except Exception as e2:
                            self.logger.error(f"작은 배치 처리 중에도 오류 발생: {e2}")
                            # 개별 문서 단위로 처리
                            for k, doc in enumerate(smaller_batch):
                                try:
                                    db.add_texts([doc.page_content], [doc.metadata])
                                    self.logger.info(f"개별 문서 처리 완료: {j+k}")
                                except Exception as e3:
                                    self.logger.error(f"문서 {j+k} 처리 실패: {e3}, 건너뜁니다.")
        
        # Chroma 0.4.x 이상에서는 자동으로 저장되므로 persist() 메서드 호출 불필요
        # 하지만 명시적으로 저장한다는 의미로 주석으로 유지
        # db.persist()
        self.logger.info("모든 문서가 DB에 저장되었습니다.")
        return db

    def load_from_db(self, embeddings):
        """Chroma DB에서 청크 로드"""
        self.logger.info("DB에서 문서 로드 중...")
        db = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=embeddings
        )
        return db

    def set_db(self, embeddings):
        """Create, save, and load db"""
        try:
            if os.path.exists(self.persist_directory):
                shutil.rmtree(self.persist_directory)
                self.logger.info(f"기존 DB 디렉토리 삭제: {self.persist_directory}")
        except Exception as e:
            self.logger.warning(f"DB 디렉토리 삭제 중 오류: {e}")

        # 디렉토리 생성
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Load docs from selected sources
        docs = self.load_documents()

        # Split Docs
        splitted_docs = self.split_docs(docs)

        # Save to DB using batch processing
        db = self.save_to_db_batch(splitted_docs, embeddings)

        return db

    def get_db(self, embeddings):
        """기존 DB 로드"""
        db = self.load_from_db(embeddings)
        return db


if __name__ == "__main__":
    pass
