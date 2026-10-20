"""Layanan temu balik dokumen (retrieval) berbasis pgvector dan filter metadata (docs/sdd.md)."""

import logging
import time
from typing import List, Optional

import psycopg

logger = logging.getLogger("umb_rag.retrieval")

from backend.app.config import settings
from backend.app.db import get_db_connection
from backend.app.schemas.chat import ChatFilter, RetrievedChunk
from backend.app.services.embedding import embed_query


RETRIEVAL_QUERY_SQL = """
SELECT id, konten, halaman, bagian, jenis_konten, topik, fakultas, program_studi, jenjang,
       1 - (embedding <=> %(vector)s::vector) AS similarity
FROM chunks
WHERE (%(bagian)s::text IS NULL OR bagian = %(bagian)s)
  AND (%(fakultas)s::text IS NULL OR fakultas = %(fakultas)s)
  AND (%(program_studi)s::text IS NULL OR program_studi = %(program_studi)s)
  AND (%(jenjang)s::text IS NULL OR jenjang = %(jenjang)s)
ORDER BY embedding <=> %(vector)s::vector ASC
LIMIT %(limit)s;
"""


def retrieve_chunks(
    query: str,
    filters: Optional[ChatFilter] = None,
    top_k: Optional[int] = None,
    threshold: Optional[float] = None,
) -> List[RetrievedChunk]:
    """Cari potongan dokumen paling relevan menggunakan cosine similarity dan filter metadata."""
    query_vector = embed_query(query)

    limit = top_k if top_k is not None else settings.top_k
    min_score = threshold if threshold is not None else settings.similarity_threshold

    filter_dict = filters.model_dump() if filters else {}
    params = {
        "vector": query_vector,
        "bagian": filter_dict.get("bagian"),
        "fakultas": filter_dict.get("fakultas"),
        "program_studi": filter_dict.get("program_studi"),
        "jenjang": filter_dict.get("jenjang"),
        "limit": limit,
    }

    results: List[RetrievedChunk] = []

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            t0 = time.perf_counter()
            cur.execute(RETRIEVAL_QUERY_SQL, params)
            rows = cur.fetchall()
            elapsed_ms = (time.perf_counter() - t0) * 1000
            logger.info("Query SQL: %d baris dalam %.1f ms", len(rows), elapsed_ms)

            for row in rows:
                score = float(row[9])
                if score < min_score:
                    continue

                results.append(
                    RetrievedChunk(
                        id=row[0],
                        konten=row[1],
                        halaman=row[2],
                        bagian=row[3],
                        jenis_konten=row[4],
                        topik=row[5],
                        fakultas=row[6],
                        program_studi=row[7],
                        jenjang=row[8],
                        similarity=round(score, 4),
                    )
                )

    return results
