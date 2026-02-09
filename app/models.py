from datetime import date, datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    status: str = Field(default="未着手")  # 未着手, 進行中, 完了
    due_date: Optional[date] = None
    priority: str = Field(default="中")  # 高, 中, 低
    progress: int = Field(default=0)  # 0-100
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class AiCoachLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
