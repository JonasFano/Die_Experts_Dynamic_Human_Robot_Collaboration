from fastapi import APIRouter, Depends, HTTPException
from .models import Experiment, Logs, UISettings, System, get_db, default_settings, update_model_from_dict
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from .schemas import (
    ExperimentBase, ExperimentCreate, ExperimentResponse, 
    LogsBase, LogsCreate, LogsResponse, 
    SystemBase, SystemCreate, SystemResponse,
    UISettingsBase, UISettingsCreate, UISettingsResponse, ActiveExperiment)

router = APIRouter(prefix="/rest")

@router.post("/experiments/", response_model=ExperimentResponse)
def create_experiment(experiment: ExperimentCreate, db: Session = Depends(get_db)):
    active_experiment = db.query(Experiment).filter(Experiment.active).first()
    if active_experiment is not None:
        raise HTTPException(status_code=403, detail="Stop the previous experiment before starting a new one.")
    db_experiment = Experiment(**experiment.dict())
    db.add(db_experiment)
    db.commit()
    db.refresh(db_experiment)
    return db_experiment

@router.post("/experiments/active", response_model=ActiveExperiment)
def get_active_experiment(db: Session = Depends(get_db)):
    active_experiment = db.query(Experiment).filter(Experiment.active).first()
    if active_experiment is None:
        return ActiveExperiment(currently_active=False)
    return ActiveExperiment(currently_active=False)

@router.post("/experiments/stop", response_model=ExperimentResponse)
def stop_experiment(db: Session = Depends(get_db)):
    active_experiment = db.query(Experiment).filter(Experiment.active).first()
    if active_experiment is not None:
        raise HTTPException(status_code=403, detail="Stop the previous experiment before starting a new one.")
    
    active_experiment.active = False
    active_experiment.end = datetime.now()
    db.commit()
    return active_experiment

@router.get("/experiments/{experiment_id}", response_model=ExperimentResponse)
def read_experiment(experiment_id: str, db: Session = Depends(get_db)):
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment

@router.get("/experiment/{experiment_id}/logs", response_model=List[LogsResponse])
def experiement_logs(experiment_id: int, db: Session = Depends(get_db)):
    log = db.query(Logs).filter(Experiment.id == experiment_id).all()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log

@router.post("/ui-settings/", response_model=UISettingsBase)
def update(ui_settings: UISettingsBase, db: Session = Depends(get_db)):
    db_ui_settings = db.query(UISettings).first()
    update_model_from_dict(db_ui_settings, ui_settings.dict(), db)
    db.commit()
    return ui_settings

@router.get("/ui-settings/", response_model=UISettingsResponse)
def read_ui_settings(db: Session = Depends(get_db)):
    ui_settings = db.query(UISettings).first()
    if not ui_settings:
        ui_settings = default_settings()
        db.add(ui_settings)
        db.commit()
    return ui_settings

@router.post("/systems/", response_model=SystemResponse)
def create_system(system: SystemCreate, db: Session = Depends(get_db)):
    db_system = System(**system.dict())
    db.add(db_system)
    db.commit()
    db.refresh(db_system)
    return db_system

@router.get("/systems/{system_id}", response_model=SystemResponse)
def read_system(system_id: int, db: Session = Depends(get_db)):
    system = db.query(System).filter(System.id == system_id).first()
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    return system

@router.post("/logs/", response_model=LogsResponse)
def create_log(log: LogsCreate, db: Session = Depends(get_db)):
    db_log = Logs(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

@router.get("/logs/{log_id}", response_model=LogsResponse)
def read_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(Logs).filter(Logs.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log
