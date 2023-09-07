import os

from langchain.document_loaders import ReadTheDocsLoader, PyPDFLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Pinecone
import pinecone

pinecone.init(
    api_key=os.environ["PINECONE_API_KEY"],
    environment=os.environ["PINECONE_ENVIRONMENT_REGION"],
)
INDEX_NAME = "langchain-doc-index"


def ingest_docs():

    # create a loader
    loader = PyPDFLoader("./langchain-docs/Tips_PerfectPayroll.pdf")

    # load your data
    raw_documents = loader.load()
    print(f"loaded {len(raw_documents)} documents")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400, chunk_overlap=50, separators=["\n\n", "\n", " ", ""]
    )
    documents = text_splitter.split_documents(raw_documents)

    print (f'You have {len(documents)} document(s) in your data')
    print (f'There are {len(documents[0].page_content)} characters in your document')

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(raw_documents)

    print (f'Now you have {len(texts)} documents')

    #for doc in documents:
    #   new_url = doc.metadata["source"]
    #   new_url = new_url.replace("langchain-docs", "https:/")
    #   doc.metadata.update({"source": new_url})

    embeddings = OpenAIEmbeddings()
    print(f"Going to add {len(documents)} to Pinecone")
    Pinecone.from_documents(documents, embeddings, index_name=INDEX_NAME)
    print("****Loading to vectorestore done ***")


if __name__ == "__main__":
    ingest_docs()