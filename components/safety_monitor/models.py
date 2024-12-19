from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import registry
from typing import Any

mapper_registry = registry()

mapper_registry.configure()

Base = declarative_base()

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def default_settings():
    return UISettings(
                distance_text=True,
                distance_line=True,
                landmarks=True,
                fixtures=True
            )


def update_model_from_dict(model_instance: Any, update_data: dict, db: Session):
    """
    Update a SQLAlchemy model instance with values from a dictionary.

    Args:
        model_instance (Any): The SQLAlchemy model instance to update.
        update_data (dict): The dictionary containing fields and their new values.
        db (Session): The SQLAlchemy database session.
    """
    for key, value in update_data.items():
        if hasattr(model_instance, key):  # Ensure the attribute exists
            setattr(model_instance, key, value)

    db.add(model_instance)  # Add the updated model instance to the session
    db.commit()  # Commit the transaction
    db.refresh(model_instance)  # Refresh the instance to reflect the changes

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def populate_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        settings = db.query(UISettings).first()
        if not settings:
            settings = default_settings()
            db.add(settings)
            db.commit()
            db.refresh(settings)
    finally:
        db.close()
        



class Experiment(Base):
    __tablename__ = 'experiment'

    id = Column(String, primary_key=True)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=True)
    description = Column(String, nullable=False)
    active = Column(Boolean, nullable=False)

    logs = relationship("Logs", back_populates="experiment")


class UISettings(Base):
    __tablename__ = 'ui_settings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    distance_text = Column(Boolean, nullable=False)
    distance_line = Column(Boolean, nullable=False)
    landmarks = Column(Boolean, nullable=False)
    fixtures = Column(Boolean, nullable=False)


class System(Base):
    __tablename__ = 'system'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    logs = relationship("Logs", back_populates="system")



class Logs(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    experiment_id = Column(Integer, ForeignKey('experiment.id'), nullable=False)
    system_id = Column(Integer, ForeignKey("system.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    value = Column(String, nullable=False)

    experiment = relationship("Experiment", back_populates="logs")
    system = relationship("System", back_populates="logs")
