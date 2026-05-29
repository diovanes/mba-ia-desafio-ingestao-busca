# Desafio MBA Engenharia de Software com IA - Full Cycle

Sistema RAG (Retrieval-Augmented Generation) para ingestão de PDF e busca semântica via CLI, usando LangChain, PostgreSQL com pgVector e Gemini.

## Pré-requisitos

- Python 3.10+
- Docker e Docker Compose
- API Key do Google (Gemini) — gratuita em [aistudio.google.com](https://aistudio.google.com)

## Configuração

### 1. Clonar e configurar variáveis de ambiente

```bash
cp .env.example .env
```

Edite o `.env` com sua chave:

```
GOOGLE_API_KEY=sua_chave_aqui
GOOGLE_EMBEDDING_MODEL=models/gemini-embedding-001
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5433/rag
PG_VECTOR_COLLECTION_NAME=documents
PDF_PATH=document.pdf
```

### 2. Criar ambiente virtual e instalar dependências

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Subir o banco de dados

```bash
docker compose up -d
```

O serviço `bootstrap_vector_ext` cria a extensão `vector` automaticamente.

### 4. Adicionar o PDF

Coloque o PDF a ser ingerido na raiz do projeto com o nome `document.pdf`.

## Execução

### Ingestão do PDF (executar uma vez)

```bash
python src/ingest.py
```

Divide o PDF em chunks de 1000 caracteres (overlap 150), gera embeddings e armazena no PostgreSQL.

### Chat via CLI

```bash
python src/chat.py
```

```
PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
RESPOSTA: O faturamento foi de 10 milhões de reais.

PERGUNTA: Qual é a capital da França?
RESPOSTA: Não tenho informações necessárias para responder sua pergunta.
```

Digite `sair` para encerrar.

## Tecnologias

- **Framework:** LangChain (LCEL)
- **Embeddings:** Google Generative AI (`models/gemini-embedding-001`)
- **LLM:** Gemini 2.5 Flash Lite (`gemini-2.5-flash-lite`)
- **Banco de dados:** PostgreSQL 17 + pgVector
- **PDF loader:** PyPDFLoader
- **Text splitter:** RecursiveCharacterTextSplitter
