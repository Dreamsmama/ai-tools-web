-- Minimal production PostgreSQL + pgvector bootstrap
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS workspaces (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS knowledge_bases (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    workspace_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    workspace_id TEXT NOT NULL,
    kb_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    file_hash TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    status TEXT NOT NULL,
    content_summary TEXT NOT NULL DEFAULT '',
    error_message TEXT NOT NULL DEFAULT '',
    retry_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

-- NOTE: replace VECTOR(128) with your configured rag_embedding_dim.
CREATE TABLE IF NOT EXISTS document_chunks (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    workspace_id TEXT NOT NULL,
    kb_id TEXT NOT NULL,
    document_id TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    metadata_json JSONB NOT NULL,
    embedding_vector VECTOR(128) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS query_logs (
    id TEXT PRIMARY KEY,
    trace_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    workspace_id TEXT NOT NULL,
    kb_id TEXT NOT NULL,
    query_text TEXT NOT NULL,
    top_k INTEGER NOT NULL,
    retrieved_chunk_ids TEXT NOT NULL,
    retrieved_chunks_json TEXT NOT NULL DEFAULT '[]',
    retrieval_latency_ms INTEGER NOT NULL DEFAULT 0,
    generation_latency_ms INTEGER NOT NULL DEFAULT 0,
    total_latency_ms INTEGER NOT NULL DEFAULT 0,
    answer TEXT NOT NULL,
    status TEXT NOT NULL,
    error_message TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_doc_scope ON documents(user_id, workspace_id, kb_id, status);
CREATE INDEX IF NOT EXISTS idx_chunk_scope ON document_chunks(user_id, workspace_id, kb_id);
CREATE INDEX IF NOT EXISTS idx_query_scope ON query_logs(user_id, workspace_id, kb_id, created_at);

-- Future ANN index example (enable after enough rows):
-- CREATE INDEX idx_chunks_embedding_ivfflat
-- ON document_chunks USING ivfflat (embedding_vector vector_cosine_ops) WITH (lists = 100);
