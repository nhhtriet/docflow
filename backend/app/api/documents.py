from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class Document(BaseModel):
    id: int
    title: str

_documents = [Document(id=1, title='Sample Document')]

@router.get('/')
async def list_documents():
    return _documents

@router.post('/')
async def create_document(doc: Document):
    _documents.append(doc)
    return doc
