from dataclasses import dataclass
from datetime import date
from hashlib import pbkdf2_hmac
from math import ceil
from os import urandom
from random import choice
from string import ascii_letters
from typing import Optional, Self

from sqlalchemy import ForeignKey, func, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import db


@dataclass
class Page[T]:
    items: list[T]
    page_count: int
    previous_page: Optional[int]
    next_page: Optional[int]

    def serialize(self):
        return {
            "items": self.items,
            "page_count": self.page_count,
            "next_page": self.next_page,
            "previous_page": self.previous_page,
        }


class IdModel(db.Base):
    __abstract__ = True

    serializable: list[str] = ["id"]

    id: Mapped[int] = mapped_column(primary_key=True)

    @classmethod
    def select(cls):
        return select(cls)

    @classmethod
    def count(cls) -> int:
        stmt = select(func.count(cls.id))
        res = db.session.execute(stmt).one()

        return res[0]

    @classmethod
    def paginate(cls, page: int, per_page: int) -> Page[Self]:
        stmt = (
            cls.select().order_by(cls.id).offset((page - 1) * per_page).limit(per_page)
        )

        items = db.session.scalars(stmt).all()

        item_count = cls.count()
        page_count = ceil(item_count / per_page)

        return Page(
            items,
            page_count,
            page - 1 if page > 1 else None,
            page + 1 if page < page_count else None,
        )

    def serialize(self):
        return {key: getattr(self, key) for key in self.serializable}

    def save(self):
        db.session.add(self)
        db.session.commit()

        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, oid: int):
        return db.session.get(cls, oid)


class User(IdModel):
    __tablename__ = "users"

    def _set_password(self, password: str):
        self.password_hash = self.hash_password(password)

    serializable = ["username"]

    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)

    password = property(fset=_set_password)

    admin: Mapped[bool] = mapped_column(default=False)

    assignments: Mapped[list["Submission"]] = relationship(back_populates="assignee")

    def __init__(self, username: str, password: str):
        self.username = username
        self._set_password(password)

    @classmethod
    def validate_password(cls, password: str):
        return len(password) >= 8

    def hash_password(self, password: str, salt: str | bytes | None = None):
        if salt is None:
            salt = urandom(32)

        key = pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        return salt + key

    def check_password(self, password: str):
        salt = self.password_hash[:32]

        return self.hash_password(password, salt) == self.password_hash

    @classmethod
    def get_by_username(cls, username: str):
        stmt = cls.select().where(cls.username == username)

        return db.session.scalar(stmt)

    def __repr__(self):
        return f"<User: {self.username}>"


class Submission(IdModel):
    __tablename__ = "submissions"

    serializable = ["title", "description", "reviewed", "assignee", "resolved"]

    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)

    reviewed: Mapped[bool] = mapped_column(default=False, nullable=False)

    assignee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    assignee: Mapped[Optional["User"]] = relationship(back_populates="assignments")
    resolved: Mapped[bool] = mapped_column(nullable=False, default=False)

    def __init__(self, title: str, description: Optional[str]):
        self.title = title
        self.description = description


class Invite(IdModel):
    __tablename__ = "invites"

    code: Mapped[str] = mapped_column(nullable=False)
    expiration: Mapped[date] = mapped_column(nullable=False)
    used: Mapped[bool] = mapped_column(default=False)

    def __init__(self, expiration: date):
        self.code = "".join(choice(ascii_letters) for _ in range(8))
        self.expiration = expiration

    @classmethod
    def get_active_invite(cls, code: str):
        stmt = (
            cls.select()
            .where(cls.expiration >= func.now())
            .where(cls.used == False)
            .where(cls.code == code)
        )

        return db.session.scalar(stmt)
