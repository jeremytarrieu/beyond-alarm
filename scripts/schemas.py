from pydantic import BaseModel


class SystemdService(BaseModel):
    launch_date: str  # mettre format iso
    id: str
    media_type: str  # mettre enum
    cmd: str
