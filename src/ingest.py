import os
import time
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH")
DATABASE_URL = os.getenv("DATABASE_URL")
COLLECTION_NAME = os.getenv("PG_VECTOR_COLLECTION_NAME")
EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL")

BATCH_SIZE = 5
BATCH_DELAY = 5   # segundos entre lotes
MAX_RETRIES = 5
RETRY_BASE_DELAY = 15  # segundos no primeiro retry (dobra a cada tentativa)


def add_batch_with_retry(vector_store, batch, lote_num, total_lotes):
    """Adiciona um lote de documentos com retry em caso de rate limit."""
    for attempt in range(MAX_RETRIES):
        try:
            vector_store.add_documents(batch)
            print(f"  Lote {lote_num}/{total_lotes} ingerido ({len(batch)} chunks)")
            return
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                wait = RETRY_BASE_DELAY * (2 ** attempt)
                print(f"  Rate limit no lote {lote_num}. Aguardando {wait}s...")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError(f"Falha ao ingerir lote {lote_num} após {MAX_RETRIES} tentativas.")


def ingest_pdf():
    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(documents)
    total = len(chunks)
    total_lotes = -(-total // BATCH_SIZE)
    print(f"{total} chunks gerados. Iniciando ingestão em lotes de {BATCH_SIZE}...")

    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)

    # Cria o store com o primeiro lote
    first_batch = chunks[:BATCH_SIZE]
    vector_store = PGVector.from_documents(
        documents=first_batch,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        connection=DATABASE_URL,
    )
    print(f"  Lote 1/{total_lotes} ingerido ({len(first_batch)} chunks)")

    for i in range(BATCH_SIZE, total, BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        lote_num = i // BATCH_SIZE + 1
        time.sleep(BATCH_DELAY)
        add_batch_with_retry(vector_store, batch, lote_num, total_lotes)

    print(f"\n{total} chunks ingeridos com sucesso.")


if __name__ == "__main__":
    ingest_pdf()
