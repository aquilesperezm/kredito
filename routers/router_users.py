
from datetime import date, timedelta
from typing import List
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from classes.models import Enumerador, Usuario, UserCreate, UserReadWithRol, UserUpdate, TipoEnumerador
from utils.manage_user import user_mgr, get_user
from fastapi_login.exceptions import InvalidCredentialsException
from database.database import get_session

router_users = APIRouter(prefix='/users', tags=['Usuarios'])


def get_users_with_rol(session: Session, usuarios: List[Usuario]) -> List[UserReadWithRol]:
    return [UserReadWithRol.from_orm(usuario, update={'rol': usuario.rol.nombre}) for usuario in usuarios]


def user_with_rol(usuario: Usuario) -> UserReadWithRol:
    return UserReadWithRol.from_orm(usuario, update={'rol': usuario.rol.nombre})

    """_summary_
        Crea un nuevo usuario en la base de datos, los parametros son
        
    - userCreate: UserCreate
    - resp: Response
    - session: Session
    - user: Usuario
    
    Returns:
        _type_: Devuelve un tipo de datos: UserReadWithRol 
    """
@router_users.post('/create')
async def create(userCreate: UserCreate, resp: Response, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> UserReadWithRol:
   
    # -------------------------------------------- Permisos ----------------------------------------------------------
    # los administradores de sucursales son root y los admin solo para sus sucursales
    rol = session.get(Enumerador,user.rol_id)
    user_id_sucursal = user.sucursal_id
     
    if rol.nombre == "Administrador" and user_id_sucursal != userCreate.sucursal_id:
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador.")
    elif rol.nombre != "Admin-Sucursal" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador... El admin solo tiene permisos en su sucursal")
   
    # ---------------------------------------------- Permisos End Block --------------------------------------------------
    
    # ----------------------------- validaciones -----------------------------------------------
        
    # Validacion #1 - si el usuario existe por el login_name, el login name no debe repetirse
    existent_user = session.query(Usuario).where(
        Usuario.login_name == userCreate.login_name).first()
  
    if existent_user is not None:
       raise HTTPException(status_code=400, detail="Error de Validación: El usuario ya existe")
    
  
    # Validacion #2 - deteccion del Rol 
    tipos_roles = session.query(TipoEnumerador).where(TipoEnumerador.nombre == "Rol de usuario").one_or_none()
    
    if tipos_roles is not None:
        rol = session.query(Enumerador).where(Enumerador.tipo_enumerador_id == tipos_roles.id).where(Enumerador.id == userCreate.rol_id).one_or_none()
    
    if rol is None:
        raise HTTPException(status_code=400, detail="Error de Validación: El rol no existe para ese id: " + str(userCreate.rol_id))
  
    # Validacion #3 - deteccion de la Sucursal
    tipos_sucursales = session.query(TipoEnumerador).where(TipoEnumerador.nombre == "Tipo de Sucursal").one_or_none()
    
    if tipos_sucursales is not None:
        sucursal = session.query(Enumerador).where(Enumerador.tipo_enumerador_id == tipos_sucursales.id).where(Enumerador.id == userCreate.sucursal_id).one_or_none()
   
    if sucursal is None:
        raise HTTPException(status_code=400, detail="Error de Validación: La Sucursal no existe para ese id: " + str(userCreate.sucursal_id))
  
     
    else: 
        user = Usuario.from_orm(userCreate)
        user.id = None
        session.add(user)
        session.commit()
        session.refresh(user)
        return user_with_rol(user)
    
 

@router_users.patch('/{usuario_id}')
async def update(usuario_id: int, user_update: UserUpdate, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> UserReadWithRol:
    
    # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------
    
    # ----------------------------- validaciones -----------------------------------------------
    
    db_user = session.get(Usuario, usuario_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Error de Validación: Usuario no encontrado")
    
        
    # Validacion #1 - si el usuario existe por el login_name, el login name no debe repetirse
    existent_user = session.query(Usuario).where(
        Usuario.login_name == user_update.login_name).first()
  
    #if existent_user is not None:
    #   raise HTTPException(status_code=400, detail="Error de Validación: El usuario ya existe")
    
  
    # Validacion #2 - deteccion del Rol 
    tipos_roles = session.query(TipoEnumerador).where(TipoEnumerador.nombre == "Rol de usuario").one_or_none()
    
    if tipos_roles is not None:
        rol = session.query(Enumerador).where(Enumerador.tipo_enumerador_id == tipos_roles.id).where(Enumerador.id == user_update.rol_id).one_or_none()
    
    if rol is None:
        raise HTTPException(status_code=400, detail="Error de Validación: El rol no existe para ese id: " + str(user_update.rol_id))
  
    # Validacion #3 - deteccion de la Sucursal
    tipos_sucursales = session.query(TipoEnumerador).where(TipoEnumerador.nombre == "Tipo de Sucursal").one_or_none()
    
    if tipos_sucursales is not None:
        sucursal = session.query(Enumerador).where(Enumerador.tipo_enumerador_id == tipos_sucursales.id).where(Enumerador.id == user_update.sucursal_id).one_or_none()
   
    if sucursal is None:
        raise HTTPException(status_code=400, detail="Error de Validación: La Sucursal no existe para ese id: " + str(user_update.sucursal_id))
    
   
    db_user.last_edited = date.today()
    
    user_data = user_update.dict(exclude_unset=True)
    for key, value in user_data.items():
        setattr(db_user, key, value)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return user_with_rol(db_user)


@router_users.post('/login')
async def login(data: OAuth2PasswordRequestForm = Depends()):
     
    username = data.username
    password = data.password

    user = await get_user(username)
    if not user:  # try with name
        raise InvalidCredentialsException
    else:
        if not user.password or password != user.password:
            raise InvalidCredentialsException
        # TODO update code here
        # TODO hash passwords
    access_token = user_mgr.create_access_token(
        data={'sub': username},
        expires=timedelta(days=145)
    )
    return {'access_token': access_token}


@router_users.get('/list')
async def get_all(session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> List[UserReadWithRol]:
    
     # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Admin-Sucursal" and rol.nombre != "Cobrador" and rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------
      
    usuarios = session.query(Usuario).all()
    return get_users_with_rol(session, usuarios)


@router_users.get('/by_id/{id_usuario}')
async def get_by_id(id_usuario: int, session: Session = Depends(get_session), user: Usuario = Depends(user_mgr)) -> UserReadWithRol:
   
     # -------------------------------------------- Permisos ----------------------------------------------------
    # solo para administradores
    rol = session.get(Enumerador,user.rol_id)
    if rol.nombre != "Admin-Sucursal" and rol.nombre != "Cobrador" and rol.nombre != "Administrador" :
        raise HTTPException(status_code=403, detail="Usuario con permisos insuficientes, contacte al administrador")

    # -------------------------------------------- Permisos -----------------------------------------------------
    
   
    db_user = session.get(Usuario, id_usuario)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user_with_rol(session.query(Usuario).get(id_usuario))


@router_users.get('/get_current')
async def get_current_logged_user(user: Usuario = Depends(user_mgr), session: Session = Depends(get_session)) -> UserReadWithRol:
   
    us = session.get(Usuario, user.id)
    return user_with_rol(us)

#

# @router_users.post('/signup')
# async def signup(usuarioSignup: UsuarioSignup, resp: Response, background_tasks: BackgroundTasks):
#     usuario_existente = await crud_usuarios.obtener_usuario_x_email(
#         usuarioSignup.email)
#     if usuario_existente is not None:
#         resp.status_code = 207
#         return {'id': -1, 'mensaje': 'Error, el correo ya está registrado.'}
#     codigo = str(randint(10000, 100000))
#     usuario_sign_up_full = UsuarioSignupFull(
#         **dict(usuarioSignup), codigo_de_registro=codigo, rol=1)
#     id_nuevo = await crud_usuarios.crear_usuario(usuario_sign_up_full)
#     if id_nuevo is None:
#         resp.status_code = 206
#     mensaje = f"""<br/>Hola,<br/>
#     Para confirmar tu registro en la aplicación DM citas médicas, haz clic en el siguiente enlace:<br/><br/> <a href="{c.URL_BASE}{c.API_PREFIX}/users/confirmar_usuario_x_web/?correo={usuario_sign_up_full.email}&codigo={codigo}" style='color:white,background-color:#1d719d;border-radius:4px,padding:5px,margin:5px'>Confirmar registro en DM cita</a>"""
#     background_tasks.add_task(
#         serv_mail.enviar_mail, usuario_sign_up_full.email, "Registro en DM - Citas", mensaje)
#     return {'id': id_nuevo}

#
#
# @usuarios_router.post('/activar_recuperar_contrasenna')
# async def activar_recuperar_contrasenna(correo: str, resp: Response, background_tasks: BackgroundTasks):
#     usuario_existente = await crud_usuarios.obtener_usuario_x_email(correo)
#     if usuario_existente is None:
#         resp.status_code = status.HTTP_406_NOT_ACCEPTABLE
#         return {'id': -1, 'mensaje': 'el correo no está registrado.'}
#     codigo = str(randint(100000000000, 1000000000000))
#     await crud_usuarios.poner_codigo_de_registro(usuario_existente.id, codigo)
#     mensaje = f"""<br/>Hola,<br/>
#     Para cambiar tu contraseña, haz clic en el siguiente enlace:<br/><br/> <a href="{c.URL_BASE}{c.API_PREFIX}/users/solicitar_cambiar_contrasenna/{codigo}/{usuario_existente.email}/" style='color:white,background-color:#1d719d;border-radius:4px,padding:5px,margin:5px'>Cambiar contraseña en DM cita</a>"""
#     background_tasks.add_task(
#         serv_mail.enviar_mail, usuario_existente.email, "Recuperar contraseña en DM - Citas", mensaje)
#     return {'mensaje': 'ok'}
#
#
# @usuarios_router.get("/solicitar_cambiar_contrasenna/{codigo}/{email}")
# async def solicitar_cambiar_contrasenna(codigo: int, email: str) -> HTMLResponse:
#     return HTMLResponse(content=serv_mail.dame_mensaje_cambiar_contrasenna(email, codigo), status_code=200)
#
#
# @usuarios_router.post('/cambiar_contrasenna')
# async def cambiar_contrasenna(resp: Response, background_tasks: BackgroundTasks, cambio_contrasenna: CambioContrasenna):
#     print('ccontrac=', cambio_contrasenna)
#     usuario_existente = await crud_usuarios.obtener_usuario_x_email(cambio_contrasenna.email)
#     if usuario_existente is None:
#         resp.status_code = 207
#         return {'id': -1, 'mensaje': 'el correo no está registrado.'}
#     esta_codigo_correcto = await crud_usuarios.esta_codigo_correcto(cambio_contrasenna.email, str(cambio_contrasenna.codigo))
#     if not esta_codigo_correcto:
#         resp.status_code = 207
#         return {'id': -2, 'mensaje': 'No se pudieron validar sus datos.'}
#     if len(cambio_contrasenna.contrasenna) < 8:
#         resp.status_code = 207
#         return {'id': -3, 'mensaje': 'la contraseña no es válida.'}
#     cambio_ok = await crud_usuarios.cambiar_contrasenna(cambio_contrasenna.email, cambio_contrasenna.contrasenna)
#     await crud_usuarios.poner_codigo_de_registro(usuario_existente.id, None)
#     return {'mensaje': 'ok'}
#
#
# @usuarios_router.post('/confirmar_usuario')
# async def confirmar_usuario(email_verification: EmailVerification) -> UsuarioConfirmadoRes:
#     usuario_confirmado = await crud_usuarios.confirmar_mail_usuario(email_verification)
#     if usuario_confirmado is None:
#         return UsuarioConfirmadoRes(mensaje='Usuario no valido', usuario_confirmado=None)
#     usuario_bd = await crud_usuarios.obtener_usuario_x_email(email_verification.email)
#     return UsuarioConfirmadoRes(mensaje='ok', usuario_confirmado=usuario_bd)
#
#
# @usuarios_router.get('/confirmar_usuario_x_web')
# async def confirmar_usuario_x_web(correo: str, codigo: str) -> HTMLResponse:
#     usuario_confirmado = await crud_usuarios.confirmar_mail_usuario_x_web(correo, codigo)
#     if usuario_confirmado is None:
#         html_content = """
#         <html>
#             <head>
#                 <title>Confirmación de correo para DM citas médicas</title>
#             </head>
#             <body>
#                 <h1><br/>Error, su correo no se ha podido confirmar.</h1>
#             </body>
#         </html>
#         """
#         return HTMLResponse(content=html_content, status_code=200)
#     html_content = """
#     <html>
#         <head>
#             <title>Confirmación de correo para DM citas médicas</title>
#         </head>
#         <body>
#         <br/><br/>
#         <h2>Su correo ha sido confirmado, ya puede iniciar sesión en DM citas médicas.</h2>
#         </body>
#     </html>
#     """
#     return HTMLResponse(content=html_content, status_code=200)
#
#


# @router_users.post('/login')
# async def login(data: OAuth2PasswordRequestForm = Depends()):
#     username = data.username
#     password = data.password

#     user = await user_mgr.dame_usuario_para_login(username)
#     if not user:
#         raise InvalidCredentialsException
#     elif password != user.contrasenna:
#         raise InvalidCredentialsException

#     access_token = user_mgr.user_mgr.create_access_token(
#         data={'sub': username},
#         expires=timedelta(days=5)
#     )
#     return {'access_token': access_token}
#
#
# @usuarios_router.get('/actual')
# async def dame_usuario(user: UsuarioBd = Depends(user_mgr)) -> Union[Usuario, None]:
#     seguros = await crud_usuarios.obtener_seguros(user.id)
#     return Usuario(**(dict(user)), seguros=seguros)
#
#
# @usuarios_router.get('/clientes')
# async def dame_clientes(user: UsuarioBd = Depends(user_mgr)) -> List[Usuario]:
#     if user.rol == c.RolUsuario.PACIENTE:
#         clientes = [await crud_usuarios.obtener_usuario_cliente_autenticado(user)]
#     elif user.rol == c.RolUsuario.SECRETARIA:
#         clientes = await crud_usuarios.obtener_usuarios_clientes_de_secretaria(user)
#         # aqui los debuelvo todos, para q alguna secretaria pueda ponerle una cita
#         # clientes = await crud_usuarios.obtener_usuarios_bd_clientes()
#     else:
#         clientes = await crud_usuarios.obtener_usuarios_bd_clientes()
#     clientes_con_seguro = []
#     for cliente in clientes:
#         seguros = await crud_usuarios.obtener_seguros(cliente.id)
#         clientes_con_seguro.append(Usuario(**(dict(cliente)), seguros=seguros))
#     return clientes_con_seguro
#
#
# @usuarios_router.post('/editar/{id_usuario}')
# async def editar(id_usuario: int, usuario_modificacion: UsuarioModificacion, user: UsuarioBd = Depends(user_mgr)) -> str:
#     res = await crud_usuarios.editar(id_usuario, usuario_modificacion)
#     return res
#
#
# @usuarios_router.post('/agregar_seguro')
# async def agregar_seguro(id_usuario: int, id_seguro: int, user: UsuarioBd = Depends(user_mgr)):
#     idCreado = await crud_usuarios.agregar_seguro(id_usuario, id_seguro)
#     return {'codigo': 200, 'id': idCreado}
#
#
# @usuarios_router.delete('/eliminar_usuario/{id_usuario}/{confirmacion}')
# async def eliminar_usuario(id_usuario: int, confirmacion: bool, response: Response, user: UsuarioBd = Depends(user_mgr)) -> ResBase:
#     if user.rol != c.RolUsuario.ADMIN:
#         response.status_code = 403
#         return ResBase(codigo=403, mensaje='No autorizado')
#
#     usuario_row = await crud_usuarios.obtener_usuario_row(id_usuario)
#     usuario_bd = UsuarioBd(**dict(usuario_row))
#     if usuario_bd.rol == c.RolUsuario.ADMIN:
#         return ResBase(codigo=403, mensaje='No se borra admin')
#     citas_usuario = await crud_citas.obtener_citas_del_usuario(id_usuario)
#     if confirmacion:
#         tx = await db.transaction()
#         try:
#             for cita in citas_usuario:
#                 res = await crud_citas.eliminar_cita(cita.id)
#                 # TODO emails a quien corresponda
#             res = await crud_usuarios.eliminar_seguros_del_usuario(id_usuario)
#             res = await crud_usuarios.eliminar_usuario(id_usuario)
#         except Exception as e:
#             print('err elim user', e)
#             await tx.rollback()
#             return ResBase(codigo=699, mensaje=f'{e}')
#         else:
#             await tx.commit()
#     else:
#         if citas_usuario:
#             response.status_code = status.HTTP_412_PRECONDITION_FAILED
#             return ResBase(codigo=status.HTTP_412_PRECONDITION_FAILED, mensaje='Citas pendientes')
#     return ResBase(codigo=200, mensaje='ok')
#
#
# @usuarios_router.delete('/eliminar_seguro_del_usuario/{id_seguro}')
# async def eliminar_seguro_del_usuario(id_seguro: int, user: UsuarioBd = Depends(user_mgr)) -> ResBase:
#     ok = await crud_usuarios.eliminar_seguro_del_usuario(id_seguro)
#     return ResBase(codigo=200, mensaje=str(ok))
