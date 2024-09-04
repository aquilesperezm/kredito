from datetime import timedelta
from fastapi import HTTPException
from fastapi_login import LoginManager
from sqlmodel import Session


from classes.models import Usuario, UserRead
from database.database import engine
from utils.exceptions import raise404_if_not

# python -c "import os; print(os.urandom(24).hex())"
SECRET = "61c4d035aa0d78acef1dddd401dd59ddc987b180c73b7098"
user_mgr = LoginManager(
    SECRET, f'/users/login', default_expiry=timedelta(days=365*10))


@user_mgr.user_loader()
async def get_user(login_name: str) -> UserRead:
    with Session(engine) as session:
        user = session.query(Usuario).where(Usuario.login_name == login_name).first()
        return user