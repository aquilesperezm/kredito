# def gen_sucesion(n: int):
#     print(n, end=', ')
#     if n == 1:
#         return 1
#     if n % 2:
#         gen_sucesion(n*3+1)
#     else:
#         gen_sucesion(n//2)


# def gen_sucesion_it(n: int):
#     while n != 1:
#         print(n, end=', ')
#         if n % 2:
#             n = n*3+1
#         else:
#             n = n//2
#     print(1)


# gen_sucesion_it(
#     1111111111111111111111111111111111111111111111111111111111111111
#     )


from datetime import timedelta
from math import floor
from typing import List
from classes.models import Credito, Cuota
from datetime import date
from dateutil.relativedelta import relativedelta
from sqlmodel import Session
from classes.models import TipoEnumerador, Enumerador
from database.database import get_session

def get_monthly_series(initial_date, num_months):
    series = [initial_date]
    current_date = initial_date

    for _ in range(num_months - 1):
        current_date += relativedelta(months=1)
        series.append(current_date)

    return series



dias_de_demora_de_cada_pago = {
    11: 1,  # diario
    12: 7,  # semanal
    13: 15,  # quincenal
    14: 30,  # mensual
}

"""
  params: fieldName_TipoCredito -> Hace referencia al nombre del tipo de enumerador 
                                   al que hace referencia el tipo de credito. Recomendaciones:
                                   Se busca en la BD cual es el tipo de enumerador que hace 
                                   referencia al tipo de credito, y el campo nombre lo 
                                   pasamos por parametro. 
  
"""
def get_dias_demora_by_pago(fieldName_TipoCredito:str, session:Session) -> dict:
    all_tipo_enumerador = session.query(TipoEnumerador).where(TipoEnumerador.nombre == fieldName_TipoCredito).first()
    id_tipocredito = all_tipo_enumerador.id
    frecuencias = session.query(Enumerador).where(Enumerador.tipo_enumerador_id == id_tipocredito).all()
    result = {}
    for f in frecuencias:
        match f.nombre:
            case 'Diario':
                result[f.id] = 1
            case 'Semanal':
                result[f.id]= 7
            case 'Quisenal':
                result[f.id] = 15
            case 'Mensual':
                result[f.id] = 30
    return result
    

def generar_cuotas_del_credito_inicialmente(credito: Credito, session: Session) -> List[Cuota]:
    total_credito = credito.monto + \
        credito.monto*(credito.tasa_de_interes/100.)
    debe_pagar_por_cuota = total_credito/credito.numero_de_cuotas
    cuotas_totales: List[Cuota] = []
    
    #print("ID Credito: ",credito.frecuencia_del_credito_id)
    
    #intervalo_entre_cuotas = dias_de_demora_de_cada_pago[credito.frecuencia_del_credito_id]
    intervalo_entre_cuotas = get_dias_demora_by_pago(fieldName_TipoCredito='Tipo de crédito',session=session)\
                                                     [credito.frecuencia_del_credito_id]
    
    for i in range(credito.numero_de_cuotas):
        delta_tiempo = relativedelta(days=(i+1)*intervalo_entre_cuotas)
        # si es mensual hacerlo x mes, no x dias
        if credito.frecuencia_del_credito_id == 14:
            delta_tiempo = relativedelta(months=i+1)
        cuotas_totales.append(
            Cuota(
                numero_de_cuota=i+1,
                fecha_de_pago=credito.fecha_de_aprobacion+delta_tiempo,
                fecha_de_aplicacion_de_mora=credito.fecha_de_aprobacion+delta_tiempo,
                valor_pagado=0,
                valor_de_cuota=debe_pagar_por_cuota,
                valor_de_mora=0,
                pagada=False
            )
        )
    return cuotas_totales
