from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Pydantic models
class ExperimentBase(BaseModel):
    id: str
    start: datetime
    end: Optional[datetime]
    description: str
    active: bool

class ExperimentCreate(ExperimentBase):
    pass

class ExperimentResponse(ExperimentBase):
    class Config:
        orm_mode = True

class ActiveExperiment(BaseModel):
    currently_active: bool

class UISettingsBase(BaseModel):
    distance_text: bool
    distance_line: bool
    landmarks: bool
    fixtures: bool

class UISettingsCreate(UISettingsBase):
    pass

class UISettingsResponse(UISettingsBase):
    id: int

    class Config:
        orm_mode = True


class SystemBase(BaseModel):
    name: str

class SystemCreate(SystemBase):
    pass

class SystemResponse(SystemBase):
    id: int

    class Config:
        orm_mode = True


class LogsBase(BaseModel):
    experiment_id: str
    system_id: int
    timestamp: datetime
    value: str

class LogsCreate(LogsBase):
    pass

class LogsResponse(LogsBase):
    id: int

    class Config:
        orm_mode = True
