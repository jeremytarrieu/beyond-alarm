from typing import List
from pydantic import BaseModel, Field, field_validator


class ServiceConfig(BaseModel):
    service_name: str = Field(..., description="The name of the systemd service.")
    command: str = Field(..., description="The command to execute.")
    parameters: List[str] = Field(default=[], description="List of parameters for the command.")
    schedule: str = Field(..., description="Schedule for the service (OnCalendar format).")

    @field_validator('service_name')
    @classmethod
    def validate_service_name(cls, v):
        if not v.isidentifier():
            raise ValueError('Service name must be a valid identifier (no spaces, special characters).')
        return v
