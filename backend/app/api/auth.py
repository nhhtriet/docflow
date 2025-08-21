from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.post('/login')
async def login(username: str, password: str):
    if not username or not password:
        raise HTTPException(status_code=400, detail='Invalid credentials')
    return {'access_token': 'dummy-token', 'token_type': 'bearer'}
