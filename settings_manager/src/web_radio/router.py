from fastapi import APIRouter

from settings_manager.src.web_radio.services import get_saved_radios

router = APIRouter(prefix='/web_radio')

@router.get('')
def get_all_the_web_radios():
    return get_saved_radios()