from fastapi import FastAPI
from .api import auth, documents

app = FastAPI(title="DocFlow API")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])

@app.get("/")
async def root():
    return {"message": "DocFlow API"}
