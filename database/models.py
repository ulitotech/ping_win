from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, func, Boolean, Integer, ForeignKey, Text
from typing import List


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Sim(Base):
    __tablename__ = 'sim'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    iccid: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    number_tel: Mapped[str] = mapped_column(String(11), nullable=False, unique=True)
    apn: Mapped[str] = mapped_column(String(40))
    ip: Mapped[str] = mapped_column(String(20))
    state: Mapped[str] = mapped_column(String(40))
    operator_id: Mapped[int] = mapped_column(ForeignKey('operator.id'), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey('project.id'), nullable=False)
    installed: Mapped[bool] = mapped_column(Boolean(), default=False)
    operator: Mapped['Operator'] = relationship(back_populates='sims')
    project: Mapped['Project'] = relationship(back_populates='sims')


class Device(Base):
    __tablename__ = 'device'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    interface: Mapped[str] = mapped_column(String(10))
    settings: Mapped[str] = mapped_column(String(250))


class Help(Base):
    __tablename__ = 'help'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(10), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)


class Project(Base):
    __tablename__ = 'project'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    port: Mapped[str] = mapped_column(String(5), nullable=False)
    sims: Mapped[List['Sim']] = relationship(back_populates='project')


class Operator(Base):
    __tablename__ = 'operator'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(10), nullable=False)
    apn: Mapped[str] = mapped_column(String(20))
    login: Mapped[str] = mapped_column(String(20))
    password: Mapped[str] = mapped_column(String(20))
    sims: Mapped[List['Sim']] = relationship(back_populates='operator')


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(Integer(), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(5), nullable=False, default='user')


class Task(Base):
    __tablename__ = 'task'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(String(500))
    phone_number: Mapped[str] = mapped_column(String(12))
    status: Mapped[int] = mapped_column(Integer(), default=0)
