from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from classes.models import Cliente, ComprobanteDePago, ComprobanteDePagoRead, Credito, Pago, PagoCreate, PagoDeCuota, PagoRead, PagoUpdate, Usuario, Enumerador
from utils.manage_user import user_mgr
from database.database import get_session
from starlette import status
from sqlalchemy import exc

router_pagos = APIRouter(prefix='/pagos', tags=['Pagos'])


@router_pagos.post('/create')
async def create(pago_create: PagoCreate, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> ComprobanteDePago:
      
    current_date = date.today()
    credito_a_pagar = session.get(Credito, pago_create.credito_id)
    
    # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Administrador" and  rol.nombre != "Cobrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------

    total_pagado = credito_a_pagar.get_total_cuotas_pagadas()
    #print("Total pagado: ", credito_a_pagar.get_valor_total_deudas_pagadas())
    
    if credito_a_pagar.monto - credito_a_pagar.get_total_cuotas_pagadas() == 0:
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED,
                            detail="Todas las deudas han sido saldadas")
    
    pago = Pago.from_orm(
        pago_create,
        {'created_at': current_date,
         'registrado_por_usuario_id': user.id}
    )
    session.add(pago)
    
    saldo = pago_create.valor_del_pago
    
    credito = session.get(Credito, pago.credito_id)
    cliente = session.get(Cliente, credito.owner_id)
    comprobante = ComprobanteDePago(cedula=cliente.numero_de_identificacion, pago=pago, cambio=saldo,
                                    nombre_del_cliente=cliente.nombres+' '+cliente.apellidos,
                                    telefono=cliente.telefono, pendiente=0, comentario=pago.comentario)
    
   
    for cuota in credito_a_pagar.cuotas:
        
        if not saldo:
            break
        
        valor_a_pagar_cuota = cuota.valor_de_cuota - cuota.valor_pagado
       
        
        if valor_a_pagar_cuota > 0:
            
            if saldo < valor_a_pagar_cuota:
                valor_a_pagar_cuota = saldo
            
            # actualizamos el saldo para las proximas cuotas
            saldo -= valor_a_pagar_cuota
                    
            # actualizamos el valor pagado de la cuota
            cuota.valor_pagado += valor_a_pagar_cuota
            
            if cuota.total_a_pagar() == cuota.valor_pagado:
                cuota.pagada = True
            
            if cuota.valor_de_cuota == cuota.valor_pagado:
                cuota.pagada = True
                
            # creamos un comprobante     
            comprobante.pagos_de_cuotas.append(PagoDeCuota(
                numero_de_cuota=cuota.numero_de_cuota, abonado=valor_a_pagar_cuota,
                tiene_mora=(cuota.valor_de_mora > 0 and (not cuota.pagada))
            ))
            
            session.add(cuota)
            session.add(comprobante)
        
            
    
    
    session.commit()
    session.refresh(pago)
    session.refresh(credito_a_pagar)
    
    comprobante.pendiente = credito.get_monto_plus_interes() - credito_a_pagar.get_total_cuotas_pagadas()
    comprobante.cambio = saldo
    session.commit()
    session.refresh(comprobante)
    return comprobante


@router_pagos.patch('/{pago_id}')
async def update(pago_id: int, pago_update: PagoUpdate, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> Pago:
    
    # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------

    
    db_pago = session.get(Pago, pago_id)
    db_pago.last_edited = date.today()
    if not db_pago:
        raise HTTPException(status_code=404, detail="Pago not found")
    pago_data = pago_update.dict(exclude_unset=True)
    for key, value in pago_data.items():
        setattr(db_pago, key, value)
    session.add(db_pago)
    session.commit()
    session.refresh(db_pago)
    return db_pago


@router_pagos.get('/list')
async def get_all(session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> List[Pago]:
    
    # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Admin-Sucursal" and rol.nombre != "Cobrador" and rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------

    return session.query(Pago).all()


@router_pagos.get('/by_id/{pago_id}')
async def pago_id(pago_id: int, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> PagoRead:
   
    # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Admin-Sucursal" and rol.nombre != "Cobrador" and rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------

    
    return session.get(Pago, pago_id)


@router_pagos.get('/comprobante_de_pago_by_id_pago/{pago_id}')
async def get_comprobante_de_pago(pago_id: int, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> ComprobanteDePagoRead:
    
    # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Admin-Sucursal" and rol.nombre != "Cobrador" and rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------

    
    return session.query(ComprobanteDePago).where(ComprobanteDePago.pago_id == pago_id).first()


@router_pagos.delete('/delete/{pago_id}')
async def remove_cliente(pago_id: int, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> Pago:
   
    # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------

    
    pago = session.get(Pago, pago_id)
    if not pago:
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED,detail="No existe el pago a borrar")
    try:
        session.delete(pago)
        session.commit()
        return pago
    except exc.SQLAlchemyError:
         raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED,detail=" Existen dependencias")
