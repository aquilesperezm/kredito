from datetime import date
import logging
from time import time
import traceback
from typing import List
from fastapi import FastAPI, Request, Depends
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi_utilities import repeat_at, repeat_every
import uvicorn
from os import getenv
from sqlmodel import SQLModel, Session
from database.database import engine
from os.path import isfile
from initial_data import generate_models_and_data
from classes.models import Cuota
from routers.router_users import router_users
from routers.router_clientes import router_clientes
from routers.router_creditos import router_creditos
from routers.router_pagos import router_pagos
from routers.router_reportes import router_reportes
from routers.router_enumeradores import router_enumeradores
from routers.router_configuracion import router_configuracion
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
from database.database import get_session
from classes.models import Usuario, Credito, Pago, Cuota,Enumerador
from utils.manage_user import user_mgr, get_user

logger = logging.getLogger("uvicorn.error")

VERSION = '0.8.9'
app = FastAPI(title='Creditos', version=VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def conectardb(request: Request, call_next):
    try:
        # await db.connect()
        response = await call_next(request)
        # await db.disconnect()
        return response
    except Exception as e:
        t = int(time())
        tb = traceback.format_exc()
        logging.exception(f'!!{t}!! : {tb}')
        return PlainTextResponse(f'ISE: {t}: {e}', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

app.mount('/static', StaticFiles(directory='static'), 'static')
app.include_router(router_users)
app.include_router(router_clientes)
app.include_router(router_creditos)
app.include_router(router_pagos)
app.include_router(router_reportes)
app.include_router(router_enumeradores)
app.include_router(router_configuracion)

# @repeat_every(seconds=20, raise_exceptions=True)
# @repeat_at('0 0 * * *')


# -------------------------------------------- Generals Endpoints -------------------------------------------------
@app.get("/resumen/get_finanzas")
async def debito_credito(session: Session = Depends(get_session), user: Usuario = Depends(user_mgr))-> dict:
    
    all_credits = session.query(Credito).all()
    result = {
        "dinero_total_plus_intereses":0.00,
        "dinero_total_without_intereses":0.00,
        "dinero_total_en_deudas":0.00,
        "dinero_total_en_pagos":0.00
              }
    
    credit:Credito
    for credit in all_credits:
        result["dinero_total_plus_intereses"] += float(credit.get_monto_plus_interes())
        result["dinero_total_without_intereses"] += float(credit.monto)
        result["dinero_total_en_deudas"] += float(credit.get_valor_total_deudas_no_pagadas())
        result["dinero_total_en_pagos"] += float(credit.total_pagado())
      
    return result
# -------------------------------------------- Generals Endpoints -------------------------------------------------


@app.on_event("startup")
@repeat_at(cron='2 2 * * *')
def actualizar_mora() -> None:
    # TODO bloquear otras instancias q recalculen la mora
    hoy = date.today()
    
    print(f'aplicando mora {hoy}')
    with Session(engine) as session:
        cuotas: List[Cuota] = session.query(
            Cuota).where(Cuota.pagada == False).all()
        
        for cuota in cuotas:
            credito = cuota.credito
            tiempo_transcurrido = hoy - cuota.fecha_de_aplicacion_de_mora
            # print(
            #     f'cuota:{cuota.id} f_semipasado= {cuota.fecha_de_aplicacion_de_mora} trasnscurrido= {tiempo_transcurrido.days}', end=' ')
            if tiempo_transcurrido.days > credito.dias_adicionales:
               
                # si el credito tiene un tipo de mora diario
                #if credito.tipo_de_mora_id == 4:  # fijo
                
                if credito.tipo_de_mora.nombre.lower() == 'diario':  # fijo
                        
                    mora = credito.valor_de_mora
                    # print(f'mora f= {mora}', end=' ')
                else:
                    mora = int((cuota.total_a_pagar()-cuota.valor_pagado) *
                               (credito.tasa_de_interes/100.))
                    # print(f'mora p= {mora}', end=' ')
                cuota.valor_de_mora += mora
                cuota.fecha_de_aplicacion_de_mora = hoy
                # print(f'aplicada mora a {cuota.id}', end=' ')
                session.add(cuota)
            # print('\n')
        session.commit()
    # print('fin aplicando mora')


@app.get('/')
def index():
    return {'Creditos': VERSION}

"""
@app.get('/test')
def test():
    return {'e': 2/0}
"""
 
# -----------------------------------------------------------------------------
"""
El parametro drop_all_tables eliminara todas las tablas y creara los datos desde 0, reiniciando todos los Ids de las tablas
"""
generate_models_and_data(drop_all_tables=True)

# ----------------------------------------------------------------------------- 

# uvicorn main:app --port 8080 --reload


if __name__ == "__main__":
    port = int(getenv("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
