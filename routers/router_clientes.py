from typing import Union
from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from classes.models import Enumerador, ClienteFilter, ClienteUpdate, Credito, Cuota, Usuario, Cliente, ClienteCreate, ClienteRead, ResumenDelCliente, ResumenDelCredito
from utils.manage_user import user_mgr
from database.database import get_session
from dateutil.relativedelta import relativedelta
from starlette import status
from sqlmodel import or_, and_, select, between

from sqlalchemy import exc

router_clientes = APIRouter(prefix='/clientes', tags=['Clientes'])


@router_clientes.post('/create')
async def create(cliente_create: ClienteCreate, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> Cliente:
    current_date = date.today()
    
    # -------------------------------------------- Permisos ----------------------------------------------------------
    # los administradores de sucursales son root y los admin solo para sus sucursales
    rol = session.get(Enumerador,user.rol_id)
    user_id_sucursal = user.sucursal_id
    
    #print("Permisos" + user_id_sucursal)
    
    if rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")
    elif rol.nombre == "Admin-Sucursal" and user_id_sucursal != cliente_create.sucursal_id:
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador... El admin solo tiene permisos en su sucursal")
    
    # ---------------------------------------------- Permisos End Block --------------------------------------------------
    
    # validar el campo tipo_de_identificacion_id de los Enumeradores (Nomencladores)
    Tipo_Identificacion = session.get(Enumerador,cliente_create.tipo_de_identificacion_id)
    if Tipo_Identificacion is None:
        raise HTTPException(status_code=400, detail="Tipo de Identificacion no encontrada")
    
    # validar la sucursal
    Sucursal = session.get(Enumerador,cliente_create.sucursal_id)
    if Sucursal is None:
        raise HTTPException(status_code=400, detail="Sucursal no encontrada")
    
    # validar el referencia_id (es una referencia recursiva, es decir a la misma tabla)
    if cliente_create.referencia_id is not None:
        Referencia = session.get(Cliente,cliente_create.referencia_id)
        if Referencia is None:
            raise HTTPException(status_code=400, detail="Referencia no encontrada, revise los clientes")
        
    cliente = Cliente.from_orm(
        cliente_create,
        {'created_at': current_date,
         'owner_id': user.id})
    
    session.add(cliente)
    session.commit()
    session.refresh(cliente)
    return cliente


@router_clientes.patch('/{cliente_id}')
async def update(cliente_id: int, cliente_update: ClienteUpdate, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> Cliente:
    db_cliente = session.get(Cliente, cliente_id)
   
    # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------
   
    # validar el campo tipo_de_identificacion_id de los Enumeradores (Nomencladores)
    Tipo_Identificacion = session.get(Enumerador,cliente_update.tipo_de_identificacion_id)
    if Tipo_Identificacion is None:
        raise HTTPException(status_code=400, detail="Tipo de Identificacion no encontrada")
    
    # validar la sucursal
    Sucursal = session.get(Enumerador,cliente_update.sucursal_id)
    if Sucursal is None:
        raise HTTPException(status_code=400, detail="Sucursal no encontrada")
    
    # validar el referencia_id (es una referencia recursiva, es decir a la misma tabla)
    if cliente_update.referencia_id is not None:
        Referencia = session.get(Cliente,cliente_update.referencia_id)
        if Referencia is None:
            raise HTTPException(status_code=400, detail="Referencia no encontrada, revise los clientes")
        
    db_cliente.last_edited = date.today()
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente not found")
    cliente_data = cliente_update.dict(exclude_unset=True)
    for key, value in cliente_data.items():
        setattr(db_cliente, key, value)
    session.add(db_cliente)
    session.commit()
    session.refresh(db_cliente)
    return db_cliente


@router_clientes.get('/list')
async def get_all(session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> List[Cliente]:
    
   # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Admin-Sucursal" and rol.nombre != "Cobrador" and rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------
   
    return session.query(Cliente).all()

    """
    Metodo para filtrar los datos de los clientes, la busqueda INCLUSIVA con todos los aspectos siguientes:
    Parametros: 
        ClienteFilter : {
             consulta : str -> Es un consulta a los campos de los clientes: 
                       - nombre
                       - apellidos
                       - numero de identificacion
                       - celular
                       - telefono
                       - email 
                       - direccion
                       - comentarios 
                       
             fecha_inicial: date -> la consulta realizada bajo este parametro es la siguiente:
               'SELECT DISTINCT credito_id FROM Cuota WHERE fecha_de_pago BETWEEN :f1 AND :f2'
                
                Se refiere a las fechas de pago de una cuota
               
             fecha_final: date -> se aplica a lo anterior
             
             en_mora: bool -> se refiere a la consulta:
              'SELECT DISTINCT credito_id FROM Cuota WHERE fecha_de_pago BETWEEN :f1 AND :f2 AND pagada = false'
             
             saldo_por_pagar: float -> se refiere a la consulta:
               'SELECT DISTINCT credito_id FROM Cuota WHERE fecha_de_pago BETWEEN :f1 AND :f2 AND pagada = false AND valor_de_mora > 0' 
           
       }
    
         Devolver todos los clientes que tengan las propiedades de consulta, ademas de un credito con fecha de pago entre fecha inicial 
         y fecha final, ademas que que tengan un saldo por pagar (valor de mora) mayor que 0

    Returns:
        _type_: Lista de tipo cliente
    """
 
def obtener_clientes_by_consulta(cliente_filter:ClienteFilter, session: Session) -> Session.query:
    text_to_query = cliente_filter.consulta
    query = session.query(Cliente).where(
           or_(
              Cliente.nombres.like(f'%{text_to_query}%'),
              Cliente.apellidos.like(f'%{text_to_query}%'),
              Cliente.numero_de_identificacion.like(f'%{text_to_query}%'),
              Cliente.celular.like(f'%{text_to_query}%'),
              Cliente.telefono.like(f'%{text_to_query}%'),
              Cliente.email.like(f'%{text_to_query}%'),
              Cliente.direccion.like(f'%{text_to_query}%'),
              Cliente.comentarios.like(f'%{text_to_query}%'),
           ))             
    return query 

def obtener_cuotas_by_cliente(cliente_filter:ClienteFilter, query:Session.query, session:Session, filter: dict = None) -> dict:
    """           
          puede ser que nos devuelva 1 o mas, entonces en caso que aparezca fecha_inicial y fecha_final, nos esta diciendo 
          que debemos buscar los creditos de todos los clientes obtenidos
          
        """
    clientes_result = query.all()
    #buscamos los creditos para esos clientes
    rel_client_credito = {}
    for client in clientes_result:
        creditos = session.query(Credito).where(Credito.owner_id == client.id).all()
        # descartamos los usuarios que no tengan creditos
        if len(list(creditos)) > 0:
            rel_client_credito[client.id] = list(creditos)          
    
    """
     Se crea un diccionario con la siguiente estructura:
     dict[id_client][credito_id] = [coutas]
    """
    
    rel_credito_cuotas = {}
    for client_key in rel_client_credito:
        creditos = rel_client_credito[client_key] 
        for credito in creditos:
            cuotas = session.query(Cuota).where(Cuota.credito_id == credito.id)
            if filter['fechas'] is not None:
                cuotas.where(between(Cuota.fecha_de_pago,cliente_filter.fecha_inicial,cliente_filter.fecha_final))
            elif filter['saldo'] is not None:
                cuotas.where(Cuota.pagada == False)
            elif filter['mora'] is not None:    
                cuotas.where(Cuota.valor_de_mora > 0)
                
            rel_credito_cuotas[client_key] = dict()
            rel_credito_cuotas[client_key][credito.id] = cuotas.all()
            
    return rel_credito_cuotas

    """
     Se puede mejorar poniendo un parametro
       - search_type:str = Query(description=" <b>Tipo de Búsqueda:</b> Inclusiva o Exclusiva", default="Inclusiva")
       Para hacer las busquedas inclusivas o exclusivas
       
    """
    
@router_clientes.post('/filtrar')
async def filtrar(cliente_filter: ClienteFilter = None,  session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> List[Cliente]:
   
    # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Admin-Sucursal" and rol.nombre != "Cobrador" and rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------
   
    query_clients = session.query(Cliente)
    
    #if search_type == 'Inclusiva':
    if cliente_filter is not None:
            
            if cliente_filter.fecha_inicial and not cliente_filter.fecha_final:
                 raise HTTPException(status_code=400, detail="Es necesario que los parametros fecha_inicial y fecha_final coexistan")
            elif not cliente_filter.fecha_inicial and cliente_filter.fecha_final:
                  raise HTTPException(status_code=400, detail="Es necesario que los parametros fecha_inicial y fecha_final coexistan")
            
            # en caso de que aparezca el paraemtro consulta
            if cliente_filter.consulta is not None and not cliente_filter.fecha_inicial and not cliente_filter.fecha_final\
                    and not cliente_filter.en_mora and not cliente_filter.saldo_por_pagar:                                        
                  query_clients = obtener_clientes_by_consulta(cliente_filter=cliente_filter, session=session)
                  return query_clients.all()
            
            # cuando existe el campo consulta, fecha inicio y fecha final  
            elif cliente_filter.consulta and cliente_filter.fecha_inicial and cliente_filter.fecha_final\
                    and not cliente_filter.en_mora and not cliente_filter.saldo_por_pagar:                                        
                  query_clients = obtener_clientes_by_consulta(cliente_filter=cliente_filter, session=session)
                  clients_by_coutas = obtener_cuotas_by_cliente(cliente_filter=cliente_filter,query=query_clients,session=session,filter={"fechas":True})
                  
                  l = []
                  for client_key in clients_by_coutas:
                      l.append(session.query(Cliente).get(client_key))
                      
                  return l
                  
            # cuando no existe la consulta pero existe fecha inicio y fecha final  
            elif not cliente_filter.consulta and cliente_filter.fecha_inicial and cliente_filter.fecha_final\
                    and not cliente_filter.en_mora and not cliente_filter.saldo_por_pagar:                                        
                  clients_by_coutas = obtener_cuotas_by_cliente(cliente_filter=cliente_filter,query=session.query(Cliente),session=session,filter={"fechas":True})
                  
                  l = []
                  for client_key in clients_by_coutas:
                      l.append(session.query(Cliente).get(client_key))
                      
                  return l
            
            # cuando no existe la consulta pero existe fecha inicio y fecha final y en mora  
            elif not cliente_filter.consulta and cliente_filter.fecha_inicial and cliente_filter.fecha_final\
                    and cliente_filter.en_mora and not cliente_filter.saldo_por_pagar:                                        
                  clients_by_coutas = obtener_cuotas_by_cliente(cliente_filter=cliente_filter,query=session.query(Cliente),session=session,filter={"fechas":True,"mora":True})
                  
                  l = []
                  for client_key in clients_by_coutas:
                      l.append(session.query(Cliente).get(client_key))
                      
                  return l
            
            # cuando no existe la consulta pero existe fecha inicio y fecha final y en mora y saldo por pagar 
            elif not cliente_filter.consulta and cliente_filter.fecha_inicial and cliente_filter.fecha_final\
                    and cliente_filter.en_mora and cliente_filter.saldo_por_pagar:                                        
                  clients_by_coutas = obtener_cuotas_by_cliente(cliente_filter=cliente_filter,query=session.query(Cliente),session=session,filter={"fechas":True,"mora":True, "saldo":True})
                  
                  l = []
                  for client_key in clients_by_coutas:
                      l.append(session.query(Cliente).get(client_key))
                      
                  return l
            
            # cuando no existe la consulta pero existe fecha inicio y fecha final y en mora y saldo por pagar 
            elif cliente_filter.consulta and cliente_filter.fecha_inicial and cliente_filter.fecha_final\
                    and cliente_filter.en_mora and cliente_filter.saldo_por_pagar:                                        
                  query_clients = obtener_clientes_by_consulta(cliente_filter=cliente_filter, session=session)
                  clients_by_coutas = obtener_cuotas_by_cliente(cliente_filter=cliente_filter,query=query_clients,session=session,filter={"fechas":True,"mora":True, "saldo":True})
                  
                  l = []
                  for client_key in clients_by_coutas:
                      l.append(session.query(Cliente).get(client_key))
                      
                  return l
            
                        
            # cuando no existen parametros  
            elif cliente_filter.consulta is None and not cliente_filter.fecha_inicial and not cliente_filter.fecha_final\
                    and not cliente_filter.en_mora and not cliente_filter.saldo_por_pagar:
                    return query_clients.all();      
                  
    # cuando no existe cuerpo para los parametros
    else:
        return query_clients.all();    
    
    #elif search_type == 'Exclusiva':
    #     pass          
    
   
@router_clientes.get('/by_id/{cliente_id}')
async def get_by_cliente_id(cliente_id: int, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> ClienteRead:
    
    # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Admin-Sucursal" and rol.nombre != "Cobrador" and rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------
   
    if cliente_id is None:
        raise HTTPException(status_code=400, detail="Es necesario el parametro de tipo query en la URL: cliente_id")
    return session.get(Cliente, cliente_id)


@router_clientes.get('/by_nit/{cliente_nit}')
async def get_by_cliente_nit(cliente_nit: int, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> List[ClienteRead]:
    
    # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Admin-Sucursal" and rol.nombre != "Cobrador" and rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------
   
    if cliente_nit is None:
        raise HTTPException(status_code=400, detail="Es necesario el parametro de tipo query en la URL: cliente_nit")
    return session.query(Cliente).where(Cliente.numero_de_identificacion == str(cliente_nit)).all()


def get_clientes_en_rango_de_fecha(fecha1: date, fecha2: date, session: Session) -> List[Cliente]:
    q = 'select distinct credito_id from Cuota where fecha_de_pago BETWEEN :f1 AND :f2'
    creditos_ids_por_pagar_en_fecha = session.execute(
        q, {'f1': f'{fecha1}', 'f2': f'{fecha2}'}).all()
    clientes_pagan_hoy = []
    clientes_pagan_hoy_ids = []
    for credit_id_list in creditos_ids_por_pagar_en_fecha:
        credito = session.get(Credito, credit_id_list[0])
        if credito.owner_id not in clientes_pagan_hoy_ids:
            clientes_pagan_hoy_ids.append(credito.owner_id)
            clientes_pagan_hoy.append(credito.owner)
    return clientes_pagan_hoy


def get_clientes_por_pagar_en_rango_de_fecha(fecha1: date, fecha2: date, session: Session) -> List[Cliente]:
    q = 'select distinct credito_id from Cuota where fecha_de_pago BETWEEN :f1 AND :f2 AND pagada = false'
    creditos_ids_por_pagar_en_fecha = session.execute(
        q, {'f1': f'{fecha1}', 'f2': f'{fecha2}'}).all()
    clientes_pagan_hoy = []
    clientes_pagan_hoy_ids = []
    for credit_id_list in creditos_ids_por_pagar_en_fecha:
        credito = session.get(Credito, credit_id_list[0])
        if credito.owner_id not in clientes_pagan_hoy_ids:
            clientes_pagan_hoy_ids.append(credito.owner_id)
            clientes_pagan_hoy.append(credito.owner)
    return clientes_pagan_hoy


def get_clientes_en_mora_en_rango_de_fecha(fecha1: date, fecha2: date, session: Session) -> List[Cliente]:
    q = 'select distinct credito_id from Cuota where fecha_de_pago BETWEEN :f1 AND :f2 AND pagada = false AND valor_de_mora > 0'
    creditos_ids_con_mora_en_fecha = session.execute(
        q, {'f1': f'{fecha1}', 'f2': f'{fecha2}'}).all()
    clientes_mora_hoy = []
    clientes_mora_hoy_ids = []
    for credit_id_list in creditos_ids_con_mora_en_fecha:
        credito = session.get(Credito, credit_id_list[0])
        if credito.owner_id not in clientes_mora_hoy_ids:
            clientes_mora_hoy_ids.append(credito.owner_id)
            clientes_mora_hoy.append(credito.owner)
    return clientes_mora_hoy

# @router_clientes.get('/por_pagar_en_rango_de_fecha/{fecha1}/{fecha2}')
# async def get_clientes_por_pagar_en_rango_de_fecha(fecha1: date, fecha2: date, session: Session = Depends(get_session), user: User = Depends(user_mgr)) -> List[Cliente]:
#     q = 'select distinct credito_id from Cuota where fecha_de_pago BETWEEN :f1 AND :f2'
#     creditos_ids_por_pagar_en_fecha = session.execute(
#         q, {'f1': f'{fecha1}', 'f2': f'{fecha2} 24'}).all()
#     clientes_pagan_hoy = []
#     clientes_pagan_hoy_ids = []
#     for credit_id_list in creditos_ids_por_pagar_en_fecha:
#         credito = session.get(Credito, credit_id_list[0])
#         if credito.owner_id not in clientes_pagan_hoy_ids:
#             clientes_pagan_hoy_ids.append(credito.owner_id)
#             clientes_pagan_hoy.append(credito.owner)
#     return clientes_pagan_hoy


# @router_clientes.get('/en_mora_en_rango_de_fecha/{fecha1}/{fecha2}')
# async def get_clientes_en_mora_en_rango_de_fecha(fecha1: date, fecha2: date, session: Session = Depends(get_session), user: User = Depends(user_mgr)) -> List[Cliente]:
#     q = 'select distinct credito_id from Cuota where fecha_de_pago BETWEEN :f1 AND :f2 AND pagada=0 AND valor_de_mora>0'
#     creditos_ids_con_mora_en_fecha = session.execute(
#         q, {'f1': f'{fecha1}', 'f2': f'{fecha2} 24'}).all()
#     clientes_mora_hoy = []
#     clientes_mora_hoy_ids = []
#     for credit_id_list in creditos_ids_con_mora_en_fecha:
#         credito = session.get(Credito, credit_id_list[0])
#         if credito.owner_id not in clientes_mora_hoy_ids:
#             clientes_mora_hoy_ids.append(credito.owner_id)
#             clientes_mora_hoy.append(credito.owner)
#     return clientes_mora_hoy


@router_clientes.get('/resumen/{cliente_id}')
async def get_resumen_de_cliente(cliente_id: int, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> ResumenDelCliente:
   
    # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------
   
    cliente = session.get(Cliente, cliente_id)
    if cliente is not None:
        resumen_de_creditos = []
        hoy = date.today()
        for credito in cliente.creditos:
            valor_de_la_mora = 0
            total_debe_pagar = 0
            cuotas_por_pagar: List[Cuota] = [
                cuota for cuota in credito.cuotas if not cuota.pagada]
            cdad_de_moras = len(
                [cuota for cuota in cuotas_por_pagar if cuota.valor_de_mora > 0])
            for cm in cuotas_por_pagar:
                debe_pagar = cm.total_a_pagar()-cm.valor_pagado
                if cm.fecha_de_pago+relativedelta(days=credito.dias_adicionales) < hoy:
                    valor_de_la_mora += debe_pagar
                total_debe_pagar += debe_pagar
            resumen_de_creditos.append(ResumenDelCredito(credito_id=credito.id,
                                                         hay_morosidad=cdad_de_moras > 0,
                                                         valor_mora=valor_de_la_mora,
                                                         total_debe_pagar=total_debe_pagar,
                                                         cant_cuota_mora=cdad_de_moras,
                                                         cuotas_por_pagar=cuotas_por_pagar
                                                         ))
        return ResumenDelCliente(cliente_id=cliente_id, nombres=cliente.nombres, apellidos=cliente.apellidos,
                                 celular=cliente.celular,
                                 documento=cliente.numero_de_identificacion,
                                 telefono=cliente.telefono,
                                 resumen_de_creditos=resumen_de_creditos)
    else: 
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='No existe el cliente')  


@router_clientes.delete('/delete/{cliente_id}')
async def remove_cliente(cliente_id: int, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> Cliente:
    
    # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------
   
    
    cliente = session.get(Cliente, cliente_id)
    if cliente is not None:
        if (len(cliente.creditos) > 0):
            raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED,
                                detail='El cliente tiene créditos en el sistema.')
        referencias = session.query(Cliente).where(
            Cliente.referencia_id == cliente.id).all()
        if (len(referencias) > 0):
            raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED,
        
                                detail='El cliente es referencia de otro cliente.')
        try:
            session.delete(cliente)
            session.commit()
            return cliente
        except exc.SQLAlchemyError:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=" Existen dependencias...")
                                     
    else: 
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No existe el cliente')  
