from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import requests
from bs4 import BeautifulSoup

# Base URL
base_url = "https://brainlox.com/courses/category/technical"

# Function to extract subpage links
def get_subpage_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    links = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if href.startswith("/courses/"):  # Adjust this condition based on actual subpage URLs
            links.append("https://brainlox.com" + href)
    
    return list(set(links))  # Remove duplicates

# Get all subpage links
subpage_urls = get_subpage_links(base_url)
print(f"Found {len(subpage_urls)} subpages.")

# Load all subpages
loaders = [WebBaseLoader(url) for url in subpage_urls]
docs = []
for loader in loaders:
    docs.extend(loader.load())

# Split documents into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(docs)

# Generate embeddings and save to FAISS
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store = FAISS.from_documents(chunks, embeddings)
vector_store.save_local("faiss_index")
print("Vector store created and saved.")
