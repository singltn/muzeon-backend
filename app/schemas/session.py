from pydantic import BaseModel, EmailStr

class SessionResponse(BaseModel):
    session_id: str
    ip: str
    browser: str
    os: str
    device: str
    is_mobile: bool
    created_at: int

class SessionListResponse(BaseModel):
    items: list[SessionResponse]
    total: int
