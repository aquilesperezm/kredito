from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from sqlalchemy import exc

from classes.models import Enumerador, TipoEnumerador, EnumeradorCreate, EnumeradorUpdate, TipoEnumeradorCreate, TipoEnumeradorRead, TipoEnumeradorUpdate, Usuario
from utils.manage_user import user_mgr
from database.database import get_session

router_enumeradores = APIRouter(prefix='/enumeradores', tags=['Enumeradores'])


@router_enumeradores.post('/tipo_enumerador_create')
async def create_tipo_enumerador(tipo_enumerador_create: TipoEnumeradorCreate, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> TipoEnumerador:
    
    # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------

    
    tipo_enumerador = TipoEnumerador.from_orm(tipo_enumerador_create)
    session.add(tipo_enumerador)
    session.commit()
    session.refresh(tipo_enumerador)
    return tipo_enumerador


@router_enumeradores.post('/enumerador_create')
async def create_enumerador(enumerador_create: EnumeradorCreate, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> Enumerador:
    
    # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------

    
    Tipo_Enumerador = session.get(TipoEnumerador,enumerador_create.tipo_enumerador_id)
    
    if Tipo_Enumerador is None:
        raise HTTPException(status_code=400, detail="Tipo de Enumerador not found")
    else: 
        enumerador = Enumerador.from_orm(enumerador_create)
        session.add(enumerador)
        session.commit()
        session.refresh(enumerador)
        
        return enumerador


@router_enumeradores.patch('/tipo_enumerador_update/{tipo_enumerador_id}')
async def update(tipo_enumerador_id: int, tipo_enumerador_update: TipoEnumeradorUpdate, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> TipoEnumerador:
    
    # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------

    
    db_tipo_enumerador = session.get(TipoEnumerador, tipo_enumerador_id)
    if not db_tipo_enumerador:
        raise HTTPException(status_code=404, detail="TipoEnumerador not found")
    tipo_enumerador_data = tipo_enumerador_update.dict(exclude_unset=True)
    for key, value in tipo_enumerador_data.items():
        setattr(db_tipo_enumerador, key, value)
    session.add(db_tipo_enumerador)
    session.commit()
    session.refresh(db_tipo_enumerador)
    return db_tipo_enumerador


@router_enumeradores.patch('/enumerador_update/{enumerador_id}')
async def update(enumerador_id: int, enumerador_update: EnumeradorUpdate, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> Enumerador:
    
    # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------

    
    db_enumerador = session.get(Enumerador, enumerador_id)
    if not db_enumerador:
        raise HTTPException(status_code=404, detail="Enumerador not found")
    enumerador_data = enumerador_update.dict(exclude_unset=True)
    for key, value in enumerador_data.items():
        setattr(db_enumerador, key, value)
    session.add(db_enumerador)
    session.commit()
    session.refresh(db_enumerador)
    return db_enumerador


@router_enumeradores.get('/tipos_de_enumerador')
async def get_all(session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> List[TipoEnumerador]:
    
    # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------

    
    return session.query(TipoEnumerador).all()


@router_enumeradores.get('/get_enumeradores/{tipo_enumerador_id}')
async def get_by_type(tipo_enumerador_id: int, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> TipoEnumeradorRead:
    
    # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------

    
    tipo_enumerador = session.get(TipoEnumerador, tipo_enumerador_id)
    return tipo_enumerador


@router_enumeradores.delete('/delete/tipo_enumerador/{tipo_enumerador_id}')
async def remove_tipo_enumerador(tipo_enumerador_id: int, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> TipoEnumerador:
   
    # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------

   
    try:
        tipo_enumerador = session.get(TipoEnumerador, tipo_enumerador_id)
        session.delete(tipo_enumerador)
        session.commit()
        return tipo_enumerador
    except exc.SQLAlchemyError:
        raise HTTPException(status_code=400, detail="Existen dependencias")


@router_enumeradores.delete('/delete/enumerador/{enumerador_id}')
async def remove_enumerador(enumerador_id: int, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> Enumerador:
    
    # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------

    
    query_enumerador = session.get(Enumerador,enumerador_id)
    if query_enumerador is None:
         raise HTTPException(status_code=400, detail="Enumerador not found")
    
    try: 
        enumerador = session.get(Enumerador, enumerador_id)
        session.delete(enumerador)
        session.commit()
    except exc.SQLAlchemyError as error:
        raise HTTPException(status_code=400, detail="Existen dependencias")
        
    return enumerador
