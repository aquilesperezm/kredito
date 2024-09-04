from datetime import date
import calendar
from typing import List,Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from classes.models import CK, Cliente, Credito, Pago, CreditoCreate, CreditoRead, CreditoUpdate, Enumerador, TipoEnumerador, Prestamo, PrestamoFiltro, Usuario, Cuota
from utils.configuracion import get_config_value
from utils.manage_user import user_mgr
from database.database import get_session
from utils import calculos
from starlette import status
from sqlmodel import or_, select
from pydantic import BaseModel
from sqlalchemy import desc, asc, exc, between

router_creditos = APIRouter(prefix='/creditos', tags=['Creditos'])

@router_creditos.post('/create')
async def create(credito_create: CreditoCreate, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> dict:
    
    # -------------------------------------------- Permisos ----------------------------------------------------------
    # los administradores de sucursales son root y los admin solo para sus sucursales
    rol = session.get(Enumerador,user.rol_id)
    user_id_sucursal = user.sucursal_id
     
    if rol.nombre == "Admin-Sucursal" and user_id_sucursal != credito_create.creador_id:
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador... El admin solo tiene permisos en su sucursal")
    elif rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")
   
    # ---------------------------------------------- Permisos End Block --------------------------------------------------

    """
    Validate fields:
       - frecuencia_del_credito_id
       - tipo_de_mora_id
       - owner_id
    """
    exist_frecuencia_credito = session.query(Enumerador).where(Enumerador.id == credito_create.frecuencia_del_credito_id).all()
    exist_tipo_mora_id = session.query(Enumerador).where(Enumerador.id == credito_create.frecuencia_del_credito_id).all()
    exist_owner_id = session.query(Cliente).where(Cliente.id == credito_create.owner_id).all()
    
    if len(exist_frecuencia_credito) == 0:
         raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail='No existe el nomenclador frecuencia del credito (frecuencia_del_credito_id)') 
    
    if len(exist_tipo_mora_id) == 0:
         raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail='No existe el nomenclador tipo de mora (tipo_de_mora_id)') 
    
    if len(exist_owner_id) == 0:
         raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail='No existe el nomenclador owner_id (owner_id)') 
    
    
    max_credito_x_cliente = int(get_config_value(session,
                                                 CK.cantidad_maxima_de_creditos_por_cliente))
    cdad_de_creditos_del_cliente = len(session.query(
        Credito, Credito.owner_id == credito_create.owner_id).all())
    if cdad_de_creditos_del_cliente >= max_credito_x_cliente:
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED,
                            detail='El cliente ha llegado al límite de créditos permitidos.')

    current_date = date.today()
    credito = Credito.from_orm(
        credito_create,
        {'created_at': current_date})
    cuotas = calculos.generar_cuotas_del_credito_inicialmente(credito=credito,session=session)
    credito.cuotas = cuotas
    
    # by kelex01
    #credito.calculate_valor_deuda()
    
    session.add(credito)
    session.commit()
    session.refresh(credito)
    
    credito_dict = credito.dict()
    credito_dict['sucursal_id'] = credito.owner.sucursal_id
    
    return credito_dict

    
@router_creditos.patch('/{credito_id}')
async def update(credito_id: int, credito_update: CreditoUpdate, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> dict:
    
    # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------

    
    if credito_update.monto != None:
       raise HTTPException(status_code=403, detail="Prohibido actualizar el campo monto")
    elif credito_update.tasa_de_interes != None:
        raise HTTPException(status_code=403, detail="Prohibido actualizar el campo tasa de interes")
    elif credito_update.valor_de_mora != None:
        raise HTTPException(status_code=403, detail="Prohibido actualizar el campo valor de mora")
    elif credito_update.frecuencia_del_credito_id != None:
        raise HTTPException(status_code=403, detail="Prohibido actualizar el campo frecuencia del credito")
    elif credito_update.tipo_de_mora_id != None:
        raise HTTPException(status_code=403, detail="Prohibido actualizar el campo tipo de mora")
      
    
    db_credito = session.get(Credito, credito_id)
    db_credito.last_edited = date.today()
    if not db_credito:
        raise HTTPException(status_code=404, detail="Credito not found")
    credito_data = credito_update.dict(exclude_unset=True)
    for key, value in credito_data.items():
        setattr(db_credito, key, value)
    
     # by kelex01
    #db_credito.calculate_valor_deuda()
        
    session.add(db_credito)
    session.commit()
    session.refresh(db_credito)
    
    credito_dict = db_credito.dict()
    credito_dict['sucursal_id'] = db_credito.owner.sucursal_id
    
    return credito_dict
    
    

    """
    
- valor_deuda_cuotas, que es la suma de las deudas de las cuotas, lo que le falta por pagar en las cuotas que ya se vencieron.
- valor_total_prestamo: valor total que debe pagar el cliente al inicio del prestamo.
- nombre_cliente: nombre del cliente
- valor_pagado: valor total pagado por el cliente hasta la fecha actual, sumatoria de los valores pagados en las cuotas
- nombre_cobrador: nombre del cobrador

Filtros:
- fecha de creacion: devuelve los prestamos creados en la fecha pasada por parametro
- id_cliente: devuelve los prestamos de un cliente en particular
- id_cobrador: devuelve los de ese cobrador
- en deuda: true/false - devuelve sólo los prestamos activos, que son los que no se han terminado de pagar

Orden:
por fecha de creacion desc, el más resiente de primero.
    
    """

class ListCreditosFilter(BaseModel):
    fecha_creacion:date = None
    cliente_id:int = None
    cobrador_id:int = None
    en_deuda:bool = None

@router_creditos.get('/list')
async def get_all(filter:ListCreditosFilter = None, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> List:
    
    # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Admin-Sucursal" and rol.nombre != "Cobrador" and rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------

    
    # Calculando el valor_deuda_cuotas: cuota está vencida si la fecha actual es mayor a la fecha de pago de la cuota 
    # y si el valor pagado es inferior al valor de la cuota más el valor de la mora   
    
    if not filter or (filter.fecha_creacion is None 
                      and filter.cliente_id is None 
                      and filter.cobrador_id is None
                      and filter.en_deuda is None
                      ):
        
        all_credits = session.query(Credito).order_by(desc(Credito.created_at)).all()
        result = []
        
        c:Credito
        for c in all_credits:
            r = dict(c)
            r['valor_deuda_cuotas'] = c.get_total_cuotas_no_pagadas()
            r['valor_total_credito'] = c.get_monto_plus_interes()
            r['nombre_cliente'] = session.get(Cliente,c.owner_id).nombres + " " + session.get(Cliente,c.owner_id).apellidos
            r['valor_pagado_cuotas'] = c.total_pagado()
            r['nombre_cobrador'] = session.get(Usuario,c.cobrador_id).nombres + " " + session.get(Usuario,c.cobrador_id).apellidos
            
            frecuencia_credito = session.query(Enumerador).where(Enumerador.id == c.frecuencia_del_credito_id).all()
            r['frecuencia_del_credito'] = list(frecuencia_credito)
            
            tipo_de_mora = session.query(Enumerador).where(Enumerador.id == c.tipo_de_mora_id).all()
            r['tipo_de_mora'] = list(tipo_de_mora)
            
            #append all cuotes and his pays
            #coutas = session.query(Cuota).where(Cuota.credito_id == c.id).all()
            #r['cuotas'] = list(coutas)
            #pagos = session.query(Pago).where(Pago.credito_id == c.id).all()
            #r['pagos'] = list(pagos)
            
            r['sucursal_id'] = c.owner.sucursal_id
            
            result.append(r)
         
        return result
    
    elif len(list(filter)) > 0:
        
        all_credits = session.query(Credito).order_by(desc(Credito.created_at)).all()
        result = []
        
        c:Credito
        for c in all_credits:
            r = dict(c)
            r['valor_deuda_cuotas'] = c.get_total_cuotas_no_pagadas()
            r['valor_total_credito'] = c.get_monto_plus_interes()
            r['nombre_cliente'] = session.get(Cliente,c.owner_id).nombres + " " + session.get(Cliente,c.owner_id).apellidos
            r['valor_pagado_cuotas'] = c.total_pagado()
            r['nombre_cobrador'] = session.get(Usuario,c.cobrador_id).nombres + " " + session.get(Usuario,c.cobrador_id).apellidos
           
            frecuencia_credito = session.query(Enumerador).where(Enumerador.id == c.frecuencia_del_credito_id).all()
            r['frecuencia_del_credito'] = list(frecuencia_credito)
            
            tipo_de_mora = session.query(Enumerador).where(Enumerador.id == c.tipo_de_mora_id).all()
            r['tipo_de_mora'] = list(tipo_de_mora)
            
            #append all cuotes and his pays
            #coutas = session.query(Cuota).where(Cuota.credito_id == c.id).all()
            #r['cuotas'] = list(coutas)
            #pagos = session.query(Pago).where(Pago.credito_id == c.id).all()
            #r['pagos'] = list(pagos)
            
            r['sucursal_id'] = c.owner.sucursal_id
           
            result.append(r)
        
        # filtro fecha_creacion
        if filter.fecha_creacion is not None:
            result = [item for item in result if item['created_at'] == filter.fecha_creacion]
        
        # filtro id_cliente
        if filter.cliente_id is not None:
            result = [item for item in result if item['owner_id'] == filter.cliente_id]
            
        # filtro id_cobrador
        if filter.cobrador_id is not None:
            result = [item for item in result if item['cobrador_id'] == filter.cobrador_id]
            
        # filtro en deuda
        if filter.en_deuda is not None:
            # obtener todos los creditos que estan en deuda
                if filter.en_deuda:
                    result = [item for item in result if item['valor_deuda_cuotas'] == 0]
                
        return result
        
        

@router_creditos.get('/by_id/{credito_id}')
async def get_by_credito_id(credito_id: int, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> dict:
    
    # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Admin-Sucursal" and rol.nombre != "Cobrador" and rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------

    
    credito_finded = session.get(Credito, credito_id)
    if credito_finded is None:
          raise HTTPException(status_code=400, detail="Credito no encontrado")
    result = dict(credito_finded)
    
    frecuencia_credito = session.query(Enumerador).where(Enumerador.id == credito_finded.frecuencia_del_credito_id).all()
    result['frecuencia_del_credito'] = list(frecuencia_credito)
            
    tipo_de_mora = session.query(Enumerador).where(Enumerador.id == credito_finded.tipo_de_mora_id).all()
    result['tipo_de_mora'] = list(tipo_de_mora)
    
    #append all cuotes and his pays
    coutas = session.query(Cuota).where(Cuota.credito_id == credito_finded.id).all()
    result['cuotas'] = list(coutas)
    pagos = session.query(Pago).where(Pago.credito_id == credito_finded.id).all()
    result['pagos'] = list(pagos)
    
    result['valor_total_credito'] = credito_finded.get_monto_plus_interes()
    result['valor_deuda_cuotas'] = credito_finded.get_total_cuotas_no_pagadas()
    result['valor_pagado_cuotas'] = credito_finded.get_total_cuotas_pagadas()
    return result


@router_creditos.get('/list_by_client/{cliente_id}')
async def get_list_by_cliente_id(cliente_id: int, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> List[CreditoRead]:
   
    # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------

   
    creditos: List[Credito] = session.query(Credito).where(
        Credito.owner_id == cliente_id).all()
    return creditos


@router_creditos.get('/cuotas_por_pagar/{credito_id}')
async def get_cuotas_por_pagar(credito_id: int, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> List[Cuota]:
    
    # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Admin-Sucursal" and rol.nombre != "Cobrador" and rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------

    
    credito = session.get(Credito, credito_id)
    return [cuota for cuota in credito.cuotas if cuota.valor_pagado < cuota.total_a_pagar()]


    
    """
    Descripcion:
        El metodo se encarga de buscar segun criterios de busqueda, los prestamos disponibles que concuerden
        con los criterios de busquedas, los prestamos son modelos abstractos que no se registran en una base de datos,
        cada prestamo esta compuesto por:
      
        Prestamo:
            - nombre del cliente -> nombre_del_cliente : str
            - id del cliente -> id_cliente: int
            - id del credito -> id_credito: int
            - fecha de cuota -> fecha_de_cuota: date      
            - valor de cuota -> valor_de_cuota: int
            - numero de cuota -> numero_de_cuota: int
            - valor de mora -> valor_de_mora: int
            - frecuencia -> frecuencia: Enumerador
            
        Requisito #1: De acuerdo a los requisitos del cliente, si no se le pasan parametros al metodo, es decir ningun criterio 
        de busqueda, devolvera todos los prestamos existentes. 
        
        Requisito #2: En caso de no pasar el filtro fecha de pago, la fecha a filtrar es la de hoy
        
        Paso #2
        Extraemos todas las cuotas que sean igual a esa fecha de pago
        
        Requisito #3: En caso de que recibir el parametro saldo_en_mora extraemos del resultado del paso #2, las
        cuotas que esten pagadas y el valor de mora sea mayor que 0
        
        Requisito #4: Si el parametro saldo_por_pagar existe, extraemos del resultado anterior, las cuotas que 
        tengan el valor pagado < que el resultado del metodo total_a_pagar()
        
        Requisito #5: si pasamos el parametro cliente, buscamos del resultado anterior, y extraemos de cada cuota el 
        propietario... y buscamos la coincidencia de cada prestamo con las cuotas, para crear una lista de prestamos        
    
    """
"""
Version vieja
@router_creditos.post('/filtrar_prestamos')
async def filtrar_prestamos(prestamo_filtro: PrestamoFiltro, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> List[Prestamo]:
   
    
    # creamos una lista para los resultados
    prestamos_result: List[Prestamo] = []
    
    # Si no se entra ningun parametro
    if prestamo_filtro.fecha_de_pago is None \
    and prestamo_filtro.saldo_por_pagar is None \
    and prestamo_filtro.saldo_en_mora is None \
    and prestamo_filtro.cliente is None \
    and prestamo_filtro.usuario_cobrador_id is None \
    and prestamo_filtro.usuario_sucursal_id is None \
    and prestamo_filtro.cliente_zona_id is None:
        
        # Consultamos todas las cuotas existentes
        listas_cuotas = session.query(Cuota).all()
        
        # por cada cuota creamos un prestamo y lo salvamos en los resultados
        for cuota in listas_cuotas:
             cliente = cuota.credito.owner
             # creamos un prestamo
             prestamo = Prestamo(id_del_credito=cuota.credito.id, id_del_cliente=cliente.id, numero_de_cuota=cuota.numero_de_cuota, fecha_de_cuota=cuota.fecha_de_pago,
                            nombre_del_cliente=f'{cliente.nombres} {cliente.apellidos}',
                            valor_de_cuota=cuota.valor_de_cuota, valor_de_la_mora=cuota.valor_de_mora,
                            frecuencia=cuota.credito.frecuencia_del_credito)
             prestamos_result.append(prestamo)
        
        # devolvemos los resultados que son una lista de prestamos     
        return prestamos_result
    
    # en caso de entrar un parametro, comenzamos a filtrar
    else:    
        
        # sino entra fecha de pago usar la fecha de hoy
        if prestamo_filtro.fecha_de_pago is None:
             hoy = date.today()
             prestamo_filtro.fecha_de_pago = hoy
        
        # obtenemos todas las cuotas por fecha
        cuotas_en_fecha: List[Cuota] = session.query(Cuota).where(Cuota.fecha_de_pago == prestamo_filtro.fecha_de_pago).all()
        
        # si existe el parametro saldo mora, la explicacion es la siguiente: por cada cuota que exista en la
        # lista si no esta pagada y su valor_mora es mayor que 0 incluyelo en el cuotas fecha que es el resultado
        if prestamo_filtro.saldo_en_mora:
            cuotas_en_fecha = [cuota for cuota in cuotas_en_fecha if (not cuota.pagada) and cuota.valor_de_mora > 0]
            
        # si existe el parametro saldo por pagar, la explicacion: por cada cuota que exista en la lista anterior llamada
        # cuotas_en_fecha, ya fue filtrada anteriormente por saldo_en_mora, incluyela en el resultado si el valor
        # pagado es menor que el total a pagar de la misma cuota
            
        if prestamo_filtro.saldo_por_pagar:
            cuotas_en_fecha = [cuota for cuota in cuotas_en_fecha if cuota.valor_pagado < cuota.total_a_pagar()]  
            
        # creamos una lista de resultados 
        cuotas_result: List[Cuota] = []
        
        # ------------------------------------------------------------------------------------------------------------
        
        # este bloque de codigo filtra las cuotas por las caracteristicas del cliente entrado, son las siguientes
            # - nombre
            # - apellidos
            # - numero_de_identificacion
            # - celular 
            # - telefono
            # - email
            # - direccion
            # - comentarios
            # - zona_id
        
        for cuota in cuotas_en_fecha:
            cliente_id = cuota.credito.owner_id
           
            if prestamo_filtro.cliente is not None:
                t = prestamo_filtro.cliente
                
                cliente = session.query(Cliente).where(
                Cliente.id == cliente_id,
                or_(
                    Cliente.nombres.like(f'%{t}%'),
                    Cliente.apellidos.like(f'%{t}%'),
                    Cliente.numero_de_identificacion.like(f'%{t}%'),
                    Cliente.celular.like(f'%{t}%'),
                    Cliente.telefono.like(f'%{t}%'),
                    Cliente.email.like(f'%{t}%'),
                    Cliente.direccion.like(f'%{t}%'),
                    Cliente.comentarios.like(f'%{t}%'),
                    Cliente.zona_id == prestamo_filtro.cliente_zona_id
                )).one_or_none()
            
                if cliente is not None:
                    cuotas_result.append(cuota)
            else:
                 cuotas_result.append(cuota)
        
        # --------------------------------------------------------------------------------------------------------
        
        # creamos una lista de prestamos que sera el resultado final
        prestamos_result: List[Prestamo] = []
        
        # para cada cuota que ha sido filtrada con todos los filtros anteriores, creamos un prestamo
        for cuota in cuotas_result:
             cliente = cuota.credito.owner
             
             prestamo = Prestamo(id_del_credito=cuota.credito.id, id_del_cliente=cliente.id, numero_de_cuota=cuota.numero_de_cuota, fecha_de_cuota=cuota.fecha_de_pago,
                            nombre_del_cliente=f'{cliente.nombres} {cliente.apellidos}',
                            valor_de_cuota=cuota.valor_de_cuota, valor_de_la_mora=cuota.valor_de_mora,
                            frecuencia=cuota.credito.frecuencia_del_credito)
             
             # Si existe el parametro cobrador_id procede a aplicar el filtro, si son iguales los ids
             if prestamo_filtro.usuario_cobrador_id is not None:
                 if cuota.credito.cobrador_id == prestamo_filtro.usuario_cobrador_id:
                    prestamos_result.append(prestamo)
             else:
                 prestamos_result.append(prestamo)
             
             # Si existe el parametro sucursal id, procede a aplicar todos los que pertenezcan a esa sucursal
             if prestamo_filtro.usuario_sucursal_id is not None:
                 if cuota.credito.cobrador.sucursal_id == prestamo_filtro.usuario_cobrador_id:
                    prestamos_result.append(prestamo)
             else:
                 prestamos_result.append(prestamo)
             
        # devuelve la lista de prestamos resultantes     
        return prestamos_result
"""

"""
Parametros de query:

    cuota_pagada = False
    sucursal_id = 22
    zona_id = 25
    fecha_de_pago = '2024-06-11'
    cobrador_id = 1
    valor_de_mora = 0
    termino_busqueda = 'smi'


"""

"""
@router_creditos.post('/filtrar_prestamos')
async def filtrar_prestamos(filtro: PrestamoFilter = None, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> List:
    
    # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Admin-Sucursal" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------

     
     # en caso de que exista el objeto filtro
     # ------------------------------------------------------------------------------------------------------------------
    
    if filtro is None:
        print('Credito Filter Debug: sin parametros')
        
        result = []
        cuotas_no_pagadas = session.query(Cuota).where(Cuota.valor_de_mora > 0).where(Cuota.pagada.is_(False)).all()
                        
        for cuota in cuotas_no_pagadas:
            temp = {}
            credito = session.get(Credito,cuota.credito_id)
            cliente = session.get(Cliente, credito.owner_id)
            frecuencia = session.get(Enumerador,credito.frecuencia_del_credito_id)
            cobrador = session.get(Usuario, credito.cobrador_id) 
             
            temp['credito_id'] = credito.id
            temp['cobrador_id'] = cobrador.id
            temp['cuota_id'] = cuota.id
            temp['cliente_id'] = cliente.id
            temp['nombre_cliente'] = cliente.nombres + " " + cliente.apellidos
            temp['valor_cuota'] = cuota.valor_de_cuota + cuota.valor_de_mora - cuota.valor_pagado
            temp['valor_mora'] = cuota.valor_de_mora 
            temp['numero_mora'] = cuota.numero_de_cuota  
            temp['fecha_de_pago'] = cuota.fecha_de_pago
            temp['sucursal_id'] = cliente.sucursal_id
            temp['zona_id'] = cliente.zona_id
            temp['frecuencia'] = frecuencia.nombre
            
            frecuencia_credito = session.query(Enumerador).where(Enumerador.id == credito.frecuencia_del_credito_id).all()
            temp['frecuencia_del_credito'] = list(frecuencia_credito)
            
            tipo_de_mora = session.query(Enumerador).where(Enumerador.id == credito.tipo_de_mora_id).all()
            temp['tipo_de_mora'] = list(tipo_de_mora)
            
            #append all cuotes and his pays
            #coutas = session.query(Cuota).where(Cuota.credito_id == credito.id).all()
            #temp['cuotas'] = list(coutas)
            
            #pagos = session.query(Pago).where(Pago.credito_id == credito.id).all()
            #temp['pagos'] = list(pagos)
            
            result.append(temp)
            
        return result
    
    # en caso de que existan parametros para filtros 
    # ------------------------------------------------------------------------------------------------------------------------
    else: 
  
    
    print('Credito Filter Debug: con parametros')
    
    result = []
    
    query = session.query(Cuota).where(Cuota.valor_de_mora > 0).where(Cuota.pagada.is_(False))
    
    # filtro para el mes
    if filtro.numero_mes is not None:
        today = date.today()
        year:str = str(today.year)
        
        range_days = calendar.monthrange(today.year,filtro.numero_mes)[1]
        #print("info: " + str(year) + ": " +str(range_days))
        
        mes:str = str(filtro.numero_mes)
        if len(mes) == 1:
            mes = "0"+mes
        
        fecha_inicio = date.fromisoformat(year+"-"+mes+"-01")
        fecha_fin = date.fromisoformat(year+"-"+mes+"-"+str(range_days))
        
        query = query.where(between(Cuota.fecha_de_pago,fecha_inicio,fecha_fin))
    
    # filtro para el valor de la mora
    if filtro.valor_de_mora is not None and filtro.valor_de_mora > 0:
        query = query.where(Cuota.valor_de_mora >= filtro.valor_de_mora) 
    else: 
         query = query.where(Cuota.valor_de_mora > 0) 
         
    # filtro para las cuotas pagadas o no
    if filtro.cuota_pagada is not None :
        query = query.where(Cuota.pagada.is_(filtro.cuota_pagada)) 
     
     # filtro para las cuotas pagadas o no
    if filtro.fecha_de_pago is not None :
        query = query.where(Cuota.fecha_de_pago == filtro.fecha_de_pago) 
    #else:
    #    query = query.where(Cuota.fecha_de_pago == date.today())      
    
    cuotas_no_pagadas = query.all()
    
    for cuota in cuotas_no_pagadas:
        temp = {}
        credito = session.get(Credito,cuota.credito_id)
        cliente = session.get(Cliente, credito.owner_id)
        frecuencia = session.get(Enumerador,credito.frecuencia_del_credito_id)
        cobrador = session.get(Usuario, credito.cobrador_id) 
        
        # filtro para el termino de busqueda
        if filtro.termino_busqueda is not None and len(filtro.termino_busqueda) > 0 :
            t = filtro.termino_busqueda
            finded = session.query(Cliente).where(
                Cliente.id == cliente.id,
                or_(
                    Cliente.nombres.like(f'%{t}%'),
                    Cliente.apellidos.like(f'%{t}%'),
                    Cliente.numero_de_identificacion.like(f'%{t}%'),
                    Cliente.celular.like(f'%{t}%'),
                    Cliente.telefono.like(f'%{t}%'),
                    Cliente.email.like(f'%{t}%'),
                    Cliente.direccion.like(f'%{t}%'),
                    Cliente.comentarios.like(f'%{t}%')
                )).one_or_none() 
        
        if finded is None:
               continue 
        
         
        temp['credito_id'] = credito.id
        temp['cobrador_id'] = cobrador.id
        temp['cuota_id'] = cuota.id
        temp['cliente_id'] = cliente.id
        temp['nombre_cliente'] = cliente.nombres + " " + cliente.apellidos
        temp['valor_cuota'] = cuota.valor_de_cuota + cuota.valor_de_mora - cuota.valor_pagado
        temp['valor_mora'] = cuota.valor_de_mora 
        temp['numero_mora'] = cuota.numero_de_cuota  
        temp['fecha_de_pago'] = cuota.fecha_de_pago
        temp['sucursal_id'] = cliente.sucursal_id
        temp['zona_id'] = cliente.zona_id
        temp['frecuencia'] = frecuencia.nombre
        
        frecuencia_credito = session.query(Enumerador).where(Enumerador.id == credito.frecuencia_del_credito_id).all()
        temp['frecuencia_del_credito'] = list(frecuencia_credito)
        
        tipo_de_mora = session.query(Enumerador).where(Enumerador.id == credito.tipo_de_mora_id).all()
        temp['tipo_de_mora'] = list(tipo_de_mora)
        
        #append all cuotes and his pays
        #coutas = session.query(Cuota).where(Cuota.credito_id == credito.id).all()
        #temp['cuotas'] = list(coutas)
        
        #pagos = session.query(Pago).where(Pago.credito_id == credito.id).all()
        #temp['pagos'] = list(pagos)
        
        result.append(temp)
            
        # filtro para la sucursal id
        if filtro.sucursal_id is not None and filtro.sucursal_id > 0:
            result = [item for item in result if item['sucursal_id'] == filtro.sucursal_id]
        elif filtro.sucursal_id == 0: 
           raise HTTPException(status_code=400, detail="ID Sucursal no puede ser 0")     
        
        # filtro para la zona id
        if filtro.zona_id is not None and filtro.zona_id > 0:
            result = [item for item in result if item['zona_id'] == filtro.zona_id]
        elif filtro.zona_id == 0:
            raise HTTPException(status_code=400, detail="ID Zona no puede ser 0")         
          
        # filtro para el cobrador id
        if filtro.cobrador_id is not None and filtro.cobrador_id > 0:
            result = [item for item in result if item['cobrador_id'] == filtro.cobrador_id]
        elif filtro.cobrador_id == 0:
           raise HTTPException(status_code=400, detail="ID Usuario Cobrador no puede ser 0")         
            
    return result   
"""

class PrestamoFilter(BaseModel):
    cuota_pagada: Optional[bool] = None
    sucursal_id: Optional[int] = None
    cobrador_id: Optional[int] = None
    zona_id: Optional[int] = None
    valor_de_mora: Optional[int] = None
    fecha_de_pago: Optional[date] = None
    termino_busqueda: Optional[str] = None
    numero_mes: Optional[int] = None

@router_creditos.post('/filtrar_prestamos')
async def filtrar_prestamos_temp(filtro: PrestamoFilter = None, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> List:
    result = list()
    
    # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Admin-Sucursal" and rol.nombre != "Cobrador" and rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------
 
    # --------------------------------------- validaciones de existencia ----------------------------------
    if filtro is not None:
        if filtro.sucursal_id is not None: 
            if filtro.sucursal_id > 0:
                result = [item for item in result if item['sucursal_id'] == filtro.sucursal_id]
            elif filtro.sucursal_id == 0: 
                raise HTTPException(status_code=400, detail="ID Sucursal no puede ser 0")     

        # filtro para la zona id
        if filtro.zona_id is not None:
            if filtro.zona_id > 0:
                result = [item for item in result if item['zona_id'] == filtro.zona_id]
            elif filtro.zona_id == 0:
                raise HTTPException(status_code=400, detail="ID Zona no puede ser 0")         

        # filtro para el cobrador id
        if filtro.cobrador_id is not None :
            if filtro.cobrador_id is not None and filtro.cobrador_id > 0:        
                result = [item for item in result if item['cobrador_id'] == filtro.cobrador_id]
            elif filtro.cobrador_id == 0:
                raise HTTPException(status_code=400, detail="ID Usuario Cobrador no puede ser 0")

        if filtro.numero_mes is not None:
            if not(filtro.numero_mes > 0 and filtro.numero_mes < 13):
                raise HTTPException(status_code=400, detail="El numero de mes debe ser mayor que 0 y menor que 13")  
    
    # --------------------------------------- validaciones de existencia ----------------------------------
   

    print('Debug Log: Filtro crear consulta')
    query = session.query(Cuota)
    
    #--------------------------------------------- Filtros ----------------------------------------------
    # filtro para el mes
    if filtro is not None:
        if filtro.numero_mes is not None:

            print('Debug Log: Filtro aplicado - filtro para el mes')

            today = date.today()
            year:str = str(today.year)

            range_days = calendar.monthrange(today.year,filtro.numero_mes)[1]

            mes:str = str(filtro.numero_mes)
            if len(mes) == 1:
                mes = "0"+mes

            fecha_inicio = date.fromisoformat(year+"-"+mes+"-01")
            fecha_fin = date.fromisoformat(year+"-"+mes+"-"+str(range_days))

            #print("Fecha filtro Inicio: " + str(fecha_inicio))
            #print("Fecha filtro Fin:" + str(fecha_fin))
            
            query = query.where(between(Cuota.fecha_de_pago,fecha_inicio,fecha_fin))
            #print(query)

        # filtro para el valor de la mora
        if filtro.valor_de_mora is not None:
            if filtro.valor_de_mora > 0:
                print('Debug Log: Filtro aplicado - filtro para el valor de la mora')
                query = query.where(Cuota.valor_de_mora >= filtro.valor_de_mora) 
        #else: 
        #     query = query.where(Cuota.valor_de_mora > 0) 

        # filtro para las cuotas pagadas o no
        if filtro.cuota_pagada is not None :
            print('Debug Log: Filtro aplicado - filtro para la cuota pagada')
            query = query.where(Cuota.pagada.is_(filtro.cuota_pagada)) 

         # filtro para la fecha de pago 
        if filtro.fecha_de_pago is not None :
            print('Debug Log: Filtro aplicado - filtro para la fecha de pago')
            query = query.where(Cuota.fecha_de_pago == filtro.fecha_de_pago) 
        #else:
        #    query = query.where(Cuota.fecha_de_pago == date.today())  

    #--------------------------------------------- Filtros ----------------------------------------------

    cuotas_no_pagadas = query.all()
    #print('Debug Log: Consulta query ' + str(len(cuotas_no_pagadas)))
    #print(cuotas_no_pagadas)
        
    for cuota in cuotas_no_pagadas:
        temp = {}
        credito = session.get(Credito,cuota.credito_id)
        cliente = session.get(Cliente, credito.owner_id)
        frecuencia = session.get(Enumerador,credito.frecuencia_del_credito_id)
        cobrador = session.get(Usuario, credito.cobrador_id) 
        
        # ------------------------------------- filtro para el termino de busqueda -----------------
        if filtro is not None and filtro.termino_busqueda is not None:
            
            print('Debug Log: Filtro aplicado - Termino de busqueda')
            
            t = filtro.termino_busqueda
            finded = session.query(Cliente).where(
                Cliente.id == cliente.id,
                or_(
                    Cliente.nombres.like(f'%{t}%'),
                    Cliente.apellidos.like(f'%{t}%'),
                    Cliente.numero_de_identificacion.like(f'%{t}%'),
                    Cliente.celular.like(f'%{t}%'),
                    Cliente.telefono.like(f'%{t}%'),
                    Cliente.email.like(f'%{t}%'),
                    Cliente.direccion.like(f'%{t}%'),
                    Cliente.comentarios.like(f'%{t}%')
                )).one_or_none() 
         
            temp['credito_id'] = credito.id
            temp['cobrador_id'] = cobrador.id
            temp['cuota_id'] = cuota.id
            temp['cliente_id'] = cliente.id
            temp['nombre_cliente'] = cliente.nombres + " " + cliente.apellidos
            temp['valor_cuota'] = cuota.valor_de_cuota + cuota.valor_de_mora - cuota.valor_pagado
            temp['valor_mora'] = cuota.valor_de_mora 
            temp['numero_mora'] = cuota.numero_de_cuota  
            temp['fecha_de_pago'] = cuota.fecha_de_pago
            temp['sucursal_id'] = cliente.sucursal_id
            temp['zona_id'] = cliente.zona_id
            temp['frecuencia'] = frecuencia.nombre
            
            frecuencia_credito = session.query(Enumerador).where(Enumerador.id == credito.frecuencia_del_credito_id).all()
            temp['frecuencia_del_credito'] = list(frecuencia_credito)
            
            tipo_de_mora = session.query(Enumerador).where(Enumerador.id == credito.tipo_de_mora_id).all()
            temp['tipo_de_mora'] = list(tipo_de_mora)
            
            if finded:
                result.append(temp)
            # ----------------------------------- filtro para la sucursal ---------------------------------------
            
            if filtro.sucursal_id is not None and filtro.sucursal_id > 0:
                result = [item for item in result if item['sucursal_id'] == filtro.sucursal_id]
            
             # ----------------------------------- filtro para la sucursal ---------------------------------------
       
            # ----------------------------------- filtro para la zona ---------------------------------------
        
            if filtro.zona_id is not None and filtro.zona_id > 0:
                result = [item for item in result if item['zona_id'] == filtro.zona_id]
               
            # ----------------------------------- filtro para la zona ---------------------------------------
        
        else:
            
            temp['credito_id'] = credito.id
            temp['cobrador_id'] = cobrador.id
            temp['cuota_id'] = cuota.id
            temp['cliente_id'] = cliente.id
            temp['nombre_cliente'] = cliente.nombres + " " + cliente.apellidos
            temp['valor_cuota'] = cuota.valor_de_cuota + cuota.valor_de_mora - cuota.valor_pagado
            temp['valor_mora'] = cuota.valor_de_mora 
            temp['numero_mora'] = cuota.numero_de_cuota  
            temp['fecha_de_pago'] = cuota.fecha_de_pago
            temp['sucursal_id'] = cliente.sucursal_id
            temp['zona_id'] = cliente.zona_id
            temp['frecuencia'] = frecuencia.nombre 
            
            frecuencia_credito = session.query(Enumerador).where(Enumerador.id == credito.frecuencia_del_credito_id).all()
            temp['frecuencia_del_credito'] = list(frecuencia_credito)
            
            tipo_de_mora = session.query(Enumerador).where(Enumerador.id == credito.tipo_de_mora_id).all()
            temp['tipo_de_mora'] = list(tipo_de_mora)
            
            result.append(temp) 

            # ----------------------------------- filtro para la sucursal ---------------------------------------
            
            if filtro.sucursal_id is not None and filtro.sucursal_id > 0:
                result = [item for item in result if item['sucursal_id'] == filtro.sucursal_id]
            
            # ----------------------------------- filtro para la sucursal ---------------------------------------
       
            # ----------------------------------- filtro para la zona ---------------------------------------
        
            if filtro.zona_id is not None and filtro.zona_id > 0:
                result = [item for item in result if item['zona_id'] == filtro.zona_id]
               
            # ----------------------------------- filtro para la zona ---------------------------------------
        
    return result


@router_creditos.delete('/delete/{credito_id}')
async def remove_cliente(credito_id: int, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> Credito:
    
    # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------

    
    try:
        credito = session.get(Credito, credito_id)
        if not credito:
            raise HTTPException(status_code=400, detail="No existe el credito a borrar") 
        session.delete(credito)
        session.commit()
        return credito
    except exc.SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail="Existen dependencias, error: " + str(e.__cause__))  
    
