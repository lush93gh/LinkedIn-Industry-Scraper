"""SQLite persistence layer (SQLModel)."""

from __future__ import annotations
from typing import List
from pathlib import Path

from sqlmodel import Field, SQLModel, Session, create_engine, select
import json


class Profile(SQLModel, table=True):
    id: str = Field(primary_key=True)  # linkedin public id, from custom URL
    headline: str | None = None
    pronouns: str | None = None
    url: str
    industry: str | None = None
    about: str | None = None
    connections: int | None = None
    open_to: str | None = None  # json string
    # Store everything else as JSON string for simplicity
    raw_json: str


class Database:
    def __init__(self, path: Path):
        self._engine = create_engine(f"sqlite:///{path}")

    def create_all(self):
        SQLModel.metadata.create_all(self._engine)

    def insert_profile(self, profile: "ProfileData") -> None:
        with Session(self._engine) as session:
            p = Profile(
                id=profile.id,
                headline=profile.headline,
                pronouns=profile.pronouns,
                url=profile.url,
                industry=profile.industry,
                about=profile.about,
                connections=profile.connections,
                open_to=json.dumps(profile.open_to) if profile.open_to else None,
                raw_json=profile.json(),
            )
            session.add(p)
            session.commit()
