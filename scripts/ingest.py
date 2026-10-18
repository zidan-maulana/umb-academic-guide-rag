"""Script skeleton for embedding and ingesting chunks into PostgreSQL + pgvector.

Pipeline (per AGENTS.md):
1. Load chunks from data/chunks/.
2. Generate embeddings via Gemini API.
3. Store chunks and vector embeddings into pgvector.
"""

def main() -> None:
    print("Ingestion script skeleton - awaiting database and embedding setup.")

if __name__ == "__main__":
    main()
