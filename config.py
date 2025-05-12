# Imports
# Env var
import os
import sys
from dotenv import load_dotenv, find_dotenv

# Env variables
sys.path.append('../..')
_ = load_dotenv(find_dotenv())

OPEN_AI_API_KEY = os.environ['OPENAI_API_KEY']

# Confluence 설정
CONFLUENCE_SPACE_NAME = os.environ['CONFLUENCE_SPACE_NAME']  # Change to your space name
CONFLUENCE_API_KEY = os.environ['CONFLUENCE_PRIVATE_API_KEY']
# https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/
CONFLUENCE_SPACE_KEY = os.environ['CONFLUENCE_SPACE_KEY']
# Hint: space_key and page_id can both be found in the URL of a page in Confluence
# https://yoursite.atlassian.com/wiki/spaces/<space_key>/pages/<page_id>
CONFLUENCE_USERNAME = os.environ['EMAIL_ADRESS']

# GitBook 설정
GITBOOK_DOMAIN = os.environ.get('GITBOOK_DOMAIN', 'https://docs.fe-ta.com')
GITBOOK_SITEMAP = os.environ.get('GITBOOK_SITEMAP', 'https://docs.fe-ta.com/sitemap-pages.xml')

# 문서 로드 옵션 (confluence, gitbook, both)
DOCUMENT_SOURCE = os.environ.get('DOCUMENT_SOURCE', 'both')

PATH_NAME_SPLITTER = './splitted_docs.jsonl'
PERSIST_DIRECTORY = './db/chroma_gitbook/'
EVALUATION_DATASET = '../data/gitbook_evaluation_dataset.tsv'
