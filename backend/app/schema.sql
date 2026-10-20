-- SKEMA TABEL CHUNKS
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS chunks (
    -- Identitas & Teks Asli
    id TEXT PRIMARY KEY,
    konten TEXT NOT NULL,
    halaman INTEGER NOT NULL,

    -- Klasifikasi & Metadata
    bagian TEXT NOT NULL,
    jenis_konten TEXT NOT NULL,
    topik TEXT,
    fakultas TEXT,
    program_studi TEXT,
    jenjang TEXT,

    -- Metadata Matkul & Akreditasi
    mata_kuliah TEXT,
    nama_inggris TEXT,
    kode_mk TEXT,
    semester INTEGER,
    sks INTEGER,
    peringkat_akreditasi TEXT,

    -- Vektor Embedding
    embedding vector(768),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Indeks filter metadata
CREATE INDEX IF NOT EXISTS idx_chunks_bagian ON chunks(bagian);
CREATE INDEX IF NOT EXISTS idx_chunks_fakultas ON chunks(fakultas);
CREATE INDEX IF NOT EXISTS idx_chunks_program_studi ON chunks(program_studi);
CREATE INDEX IF NOT EXISTS idx_chunks_jenis_konten ON chunks(jenis_konten);
