import os
from dotenv import load_dotenv
from supabase.client import Client, create_client
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import SupabaseVectorStore
from langchain.document_loaders import TextLoader
from langchain.schema import Document
from git import Repo
from git_embed import get_list_of_commits

load_dotenv()

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# configure these to fit your needs
exclude_dir = ['.git', 'node_modules', 'public', 'assets']
exclude_files = ['package-lock.json', '.DS_Store']
exclude_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.ico', '.svg', '.webp',
                      '.mp3', '.wav']

documents = []

for dirpath, dirnames, filenames in os.walk('repo'):
    # skip directories in exclude_dir
    dirnames[:] = [d for d in dirnames if d not in exclude_dir]

    for file in filenames:
        _, file_extension = os.path.splitext(file)

        # skip files in exclude_files
        if file not in exclude_files and file_extension not in exclude_extensions:
            file_path = os.path.join(dirpath, file)
            loader = TextLoader(file_path, encoding='ISO-8859-1')
            documents.extend(loader.load())


text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
docs = text_splitter.split_documents(documents)

for doc in docs:
    source = doc.metadata['source']
    cleaned_source = '/'.join(source.split('/')[1:])
    doc.page_content = "FILE NAME: " + cleaned_source + \
        "\n###\n" + doc.page_content.replace('\u0000', '')

commits_list = get_list_of_commits(Repo('repo'))

def get_text_chunks_langchain(text):
   text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=100)
   docs = text_splitter.split_text(text)
   return docs

for commit in commits_list:
    chunks = get_text_chunks_langchain(commit['diff'])
    for chunk in chunks:
        doc = Document(
            page_content="COMMIT MESSAGE: " + commit['commit'] + "\n###\n" + chunk,
            metadata={'commit_message': commit['commit']}
        )
        docs.append(doc)

embeddings = OpenAIEmbeddings()

vector_store = SupabaseVectorStore.from_documents(
    docs,
    embeddings,
    client=supabase,
    table_name=os.environ.get("TABLE_NAME"),
)
