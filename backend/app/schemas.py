from datetime import date
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

Status = Literal["Applied", "Interview", "Offer", "Rejected"]


class ApplicationBase(BaseModel):
    company: str
    role: str
    status: Status = "Applied"
    job_url: Optional[str] = None
    applied_on: Optional[date] = None
    notes: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    status: Optional[Status] = None
    job_url: Optional[str] = None
    applied_on: Optional[date] = None
    notes: Optional[str] = None


class ApplicationOut(ApplicationBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: str
    password: str = Field(min_length=8)


class UserOut(BaseModel):
    id: int
    email: str
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str