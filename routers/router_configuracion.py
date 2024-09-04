from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from classes.models import Configuracion, ConfiguracionUpdate, Usuario, Enumerador
from utils.manage_user import user_mgr
from database.database import get_session

router_configuracion = APIRouter(
    prefix='/configuracion', tags=['Configuracion'])


@router_configuracion.patch('/')
async def update(configuracionUpdate: ConfiguracionUpdate, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> Configuracion:
    
    # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------
   
    config_entry = session.query(Configuracion).where(
        Configuracion.key == configuracionUpdate.key).first()
    if config_entry is None:
        raise HTTPException(status_code=404, detail="Key not found")
    config_entry.value = configuracionUpdate.value
    session.add(config_entry)
    session.commit()
    session.refresh(config_entry)
    return config_entry

"""
@router_configuracion.get('/keys')
async def get_keys(session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> List[str]:
    return [c.key for c in session.query(Configuracion).all()]


@router_configuracion.get('/by_key/{key}')
async def get_config(key: str, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> str:
    config = session.query(Configuracion).where(
        Configuracion.key == key).first()
    if config is None:
        raise HTTPException(status_code=404, detail="Key not found")
    return config.value
"""