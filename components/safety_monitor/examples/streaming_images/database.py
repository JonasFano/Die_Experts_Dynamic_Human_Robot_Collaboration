import datetime
from sqlalchemy import create_engine, Column, Integer, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.create_all(bind=engine)


class UISettings(Base):
    __tablename__ = "ui_settings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    show_fixture_state = Column(Boolean, default=False)
    show_text = Column(Boolean, default=False)
    show_points = Column(Boolean, default=False)


class Experiment(Base):
    __tablename__ = "experiments"
    id = Column(
        Integer, primary_key=True, autoincrement=True
    )  # Maps to id with auto-increment
    start = Column(DateTime, default=datetime.now)
    end = Column(DateTime, nullable=True)
    active = Column(Boolean, default=True)
