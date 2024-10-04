from fastapi import APIRouter

from backend.src.web_radio.schemas import WebRadio
from backend.src.web_radio.services import get_saved_radios

router = APIRouter(prefix='/web_radio')

@router.get('')
def get_all_the_web_radios():
    return get_saved_radios()