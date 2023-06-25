import os
from dotenv import load_dotenv
from supabase.client import Client, create_client
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import SupabaseVectorStore
from langchain.document_loaders import TextLoader
from langchain.schema import Document
from git import Repo

load_dotenv()

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def get_list_of_commits(repo: Repo):
    commits = list(repo.iter_commits())
    commits.reverse()
    commit_docs = []

    for i in range(0, len(commits) - 1):
        older_commit = commits[i]
        newer_commit = commits[i + 1]
        commit_str = newer_commit.message
        diff_str = repo.git.diff(older_commit, newer_commit)
        commit_docs.append({"commit": commit_str, "diff": diff_str})

    return commit_docs
