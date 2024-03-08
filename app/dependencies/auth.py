from typing import Annotated
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from ..utils import decode_access_token

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/')

async def get_current_user1(authorization: str = Header(...)):
    try:
        token = authorization.replace("Bearer ","")
        payload = decode_access_token(token)
        email: str|None = payload.get('sub')
        user_id: int|None = payload.get('id')
        role: str|None = payload.get('role')
        if email is None or user_id is None:
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
        
        return {'email':email, 'id': user_id, 'role': role}
    except JWTError:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
    
async def get_current_user(token:Annotated[str, Depends(oauth2_bearer)]):
    print("get current user")
    return {'email':"krishna@test.com", 'id': 1, 'role': "admin"}
    try:
        payload = decode_access_token(token)
        print(payload)
        email: str|None = payload.get('sub')
        user_id: int|None = payload.get('id')
        role: str|None = payload.get('role')
        if email is None or user_id is None:
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
        
        return {'email':email, 'id': user_id, 'role': role}
    except JWTError:
        print("jwt error")
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
