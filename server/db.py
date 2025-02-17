import os
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlmodel import Field, Session, SQLModel, create_engine


class Link(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    url: str
    status: bool = False
    last_checked: datetime = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))


engine = create_engine(
    os.environ.get("CRON_DATABASE_URL"), echo=True, pool_pre_ping=True
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    create_db_and_tables()
    return Session(engine)
