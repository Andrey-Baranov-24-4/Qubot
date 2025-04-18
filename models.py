from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    BigInteger,
    ForeignKey,
    func,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# Таблица с пользователями
class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    telegram_id = Column(BigInteger, unique=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    # связь с таблицей запросов
    requests = relationship("Request", back_populates="user", cascade="all, delete-orphan")


# Таблица с запросами пользователей
class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="requests")
