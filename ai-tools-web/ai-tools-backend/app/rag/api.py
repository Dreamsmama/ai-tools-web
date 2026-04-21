from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.rag.document_service import document_service
from app.rag.kb_service import kb_service
from app.rag.qa_service import rag_qa_service
from app.rag.schemas import AskRequest, Envelope, KnowledgeBaseCreateRequest
from app.rag.scope import RequestScope, get_request_scope

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/kbs", response_model=Envelope)
async def create_kb(
    body: KnowledgeBaseCreateRequest,
    scope: RequestScope = Depends(get_request_scope),
) -> Envelope:
    kb = kb_service.create(scope, body.name, body.description)
    return Envelope(code=0, data=kb)


@router.get("/kbs", response_model=Envelope)
async def list_kbs(scope: RequestScope = Depends(get_request_scope)) -> Envelope:
    return Envelope(code=0, data=kb_service.list(scope))


@router.post("/documents/upload", response_model=Envelope)
async def upload_document(
    kb_id: str = Form(...),
    file: UploadFile = File(...),
    scope: RequestScope = Depends(get_request_scope),
) -> Envelope:
    payload = await file.read()
    doc = await document_service.upload(
        scope=scope,
        kb_id=kb_id,
        filename=file.filename or "unknown.txt",
        mime_type=file.content_type or "application/octet-stream",
        file_bytes=payload,
    )
    return Envelope(code=0, data=doc)


@router.post("/documents/{document_id}/ingest", response_model=Envelope)
async def ingest_document(
    document_id: str,
    scope: RequestScope = Depends(get_request_scope),
) -> Envelope:
    try:
        doc = await document_service.ingest(scope, document_id)
        return Envelope(code=0, data=doc)
    except Exception as err:
        return Envelope(code=500, message=f"ingest failed: {str(err)[:300]}")


@router.post("/documents/{document_id}/retry", response_model=Envelope)
async def retry_document(
    document_id: str,
    scope: RequestScope = Depends(get_request_scope),
) -> Envelope:
    try:
        doc = await document_service.retry(scope, document_id)
        return Envelope(code=0, data=doc)
    except Exception as err:
        return Envelope(code=500, message=f"retry failed: {str(err)[:300]}")


@router.get("/documents/{document_id}", response_model=Envelope)
async def get_document(document_id: str, scope: RequestScope = Depends(get_request_scope)) -> Envelope:
    doc = document_service.get(scope, document_id)
    return Envelope(code=0, data=doc)


@router.post("/ask", response_model=Envelope)
async def ask(body: AskRequest, scope: RequestScope = Depends(get_request_scope)) -> Envelope:
    try:
        result = await rag_qa_service.ask(
            scope=scope,
            kb_id=body.kb_id,
            query=body.query,
            top_k=body.top_k,
        )
        return Envelope(code=0, data=result.model_dump())
    except Exception as err:
        return Envelope(code=500, message=f"ask failed: {str(err)[:300]}")
