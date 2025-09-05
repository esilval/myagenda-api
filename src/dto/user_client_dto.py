from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel


class UserClientCreateDTO(BaseModel):
    client_id: str
    user_id: str


class UserClientDTO(UserClientCreateDTO):
    id: str
    created_at: datetime

