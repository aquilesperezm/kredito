from sqlmodel import SQLModel
from typing import List
from database.database import engine, Session
from classes.models import CK, Configuracion, Cuota ,Exportacion, ParamExportacion, Usuario,\
    TipoEnumerador, Enumerador, ClienteCreate, Cliente, Credito, PagoDeCuota, ComprobanteDePago, Pago, ExportacionByUser
from fastapi.testclient import TestClient

    

def generate_models_and_data(drop_all_tables = False):
    with Session(engine) as session:
        # enums
       
        if drop_all_tables:
            print("Log: Eliminando tablas y todos sus datos de la BD")
            SQLModel.metadata.drop_all(engine)

            print("Log: Creando tablas de acuerdo al ORM - BD")
            SQLModel.metadata.create_all(engine)
            print('Log: Modelos creados con exito')
        
        else: 
            
            print("Log: Eliminando datos de la BD")
            
            session.query(ExportacionByUser).delete()
            
            session.query(ComprobanteDePago).delete()
            session.query(PagoDeCuota).delete()
            session.query(Pago).delete()
            session.query(Cuota).delete()
            session.query(Credito).delete()
            session.query(Cliente).delete()
            session.query(Usuario).delete()
            
           
            
            session.query(Enumerador).delete()
            session.query(TipoEnumerador).delete()
        
            session.query(Configuracion).delete()
            session.query(ParamExportacion).delete()
            session.query(Exportacion).delete()
              
         
        # Se adiciona el tipo de nomenclador: Rol de Usuario
        rol_de_usuario = TipoEnumerador(nombre='Rol de usuario')
        
        # Se adicionan los nomencladores (Enumerador) de tipo Rol de usuario
        rol_admin = Enumerador(tipo_enumerador=rol_de_usuario, nombre='Administrador')
        rol_admin_sucursal = Enumerador(tipo_enumerador=rol_de_usuario, nombre='Admin-Sucursal')
        rol_cobrador = Enumerador(tipo_enumerador=rol_de_usuario, nombre='Cobrador')
        
        # Adicionamos en la Base de datos
        session.add_all([rol_de_usuario, rol_admin,rol_de_usuario, rol_cobrador])

        # Adicionamos un tipo de nomenclador: Tipo de identificacion
        tipo_de_identificacion = TipoEnumerador(nombre='Tipo de identificación')
        
        # Adicionamos los nomencladores de tipo de identificacion
        identificacion_por_cedula = Enumerador(nombre='Cédula', tipo_enumerador=tipo_de_identificacion)
        identificacion_por_cedula_extranjera = Enumerador(nombre='Cédula Extranjera', tipo_enumerador=tipo_de_identificacion)
        identificacion_por_pasaporte = Enumerador(nombre='Pasaporte', tipo_enumerador=tipo_de_identificacion)
        identificacion_por_nit = Enumerador(nombre='Nit', tipo_enumerador=tipo_de_identificacion)
        identificacion_por_tarjeta_de_identidad = Enumerador(nombre='Tarjeta de identidad', tipo_enumerador=tipo_de_identificacion)
        
        # Adicionamos en la Base de Datos
        session.add_all([tipo_de_identificacion, identificacion_por_cedula,
                        identificacion_por_cedula_extranjera, identificacion_por_pasaporte,
                        identificacion_por_nit, identificacion_por_tarjeta_de_identidad])

        # Adicionamos un tipo de Enumerador: Estado
        tipo_de_estado = TipoEnumerador(nombre='Estado')
        
        # Adicionamos los nomencladores de tipo Estado
        estado_activo = Enumerador(nombre='Activo', tipo_enumerador=tipo_de_estado)
        estado_inactivo = Enumerador(nombre='Inactivo', tipo_enumerador=tipo_de_estado)
        
        # Adicionamos en la base de datos
        session.add_all([tipo_de_estado, estado_activo, estado_inactivo])

        # Adicionamos un tipo de Enumerador: Tipo de Creadito
        frecuencia_del_credito = TipoEnumerador(nombre='Tipo de crédito')
        
        # Adicionamos los nomencladores: Tipo de credito
        credito_diario = Enumerador(nombre='Diario', tipo_enumerador=frecuencia_del_credito)
        credito_semanal = Enumerador(nombre='Semanal', tipo_enumerador=frecuencia_del_credito)
        credito_quincenal = Enumerador( nombre='Quincenal', tipo_enumerador=frecuencia_del_credito)
        credito_mensual = Enumerador(nombre='Mensual', tipo_enumerador=frecuencia_del_credito)
        
        # Adicionamos a la base de datos
        session.add_all([frecuencia_del_credito, credito_diario,
                        credito_semanal, credito_quincenal, credito_mensual])

        # Adicionamos un tipo de nomenclador: Metodo de pago
        metodo_de_pago = TipoEnumerador(nombre='Método de pago')
        
        # Adicionamos los nomencladores: Metodo de pago
        pago_en_efectivo = Enumerador( nombre='Efectivo', tipo_enumerador=metodo_de_pago)
        pago_en_transferencia = Enumerador(nombre='Transferencia', tipo_enumerador=metodo_de_pago)
        pago_en_cheque = Enumerador(nombre='Cheque', tipo_enumerador=metodo_de_pago)
        pago_en_item = Enumerador( nombre='Item', tipo_enumerador=metodo_de_pago)
        pago_en_tarjeta_debito = Enumerador(nombre='Tarjeta de débito', tipo_enumerador=metodo_de_pago)
        pago_en_tarjeta_credito = Enumerador(nombre='Tarjeta de crédito', tipo_enumerador=metodo_de_pago)
        pago_en_otros = Enumerador( nombre='Otros', tipo_enumerador=metodo_de_pago)
        
        # Adicionamos a la base de datos
        session.add_all([metodo_de_pago, pago_en_efectivo, pago_en_transferencia, pago_en_cheque, pago_en_item,
            pago_en_tarjeta_debito,
            pago_en_tarjeta_credito,
            pago_en_otros,
        ])

        # Adicionamos un tipo de Nomenclador: Tipo de mora
        tipo_de_mora = TipoEnumerador( nombre='Tipo de mora')
        
        # Adicionamos los nomencladores de tipo: Tipo de mora
        mora_fija = Enumerador( nombre='Valor fijo', tipo_enumerador=tipo_de_mora)
        mora_en_porciento = Enumerador( nombre='Porciento', tipo_enumerador=tipo_de_mora)
        
        # Adicionamos un tipo de Nomenclador: Tipo de Sucursal
        tipo_de_sucursal = TipoEnumerador( nombre='Tipo de Sucursal')
        
        # Adicionamos los nomencladores de Tipo de Sucursal
        sucursal_1 = Enumerador(nombre='Sucursal#1', tipo_enumerador=tipo_de_sucursal)
        sucursal_2 = Enumerador(nombre='Sucursal#2', tipo_enumerador=tipo_de_sucursal)
        sucursal_3 = Enumerador(nombre='Sucursal#3', tipo_enumerador=tipo_de_sucursal)
        
        session.add_all([tipo_de_sucursal,sucursal_1,sucursal_2,sucursal_3])
        
        # Adicionamos un tipo de Nomenclador: Tipo de Sucursal
        tipo_de_zona = TipoEnumerador( nombre='Tipo de Zona')
        
        # Adicionamos los nomencladores de Tipo de Sucursal
        zona_1_Nibaje = Enumerador(nombre='Nibaje', tipo_enumerador=tipo_de_zona)
        zona_2_villa_olimpica = Enumerador(nombre='La Villa olímpica', tipo_enumerador=tipo_de_zona)
        zona_3_cruz_marylopez = Enumerador(nombre='Cruz De Mari López', tipo_enumerador=tipo_de_zona)
        zona_4_Pekin = Enumerador(nombre='Pekín', tipo_enumerador=tipo_de_zona)
        zona_5_CienFuegos = Enumerador(nombre='Cien fuegos', tipo_enumerador=tipo_de_zona)
        zona_6_Gurabo = Enumerador(nombre='Gurabo', tipo_enumerador=tipo_de_zona)
        zona_7_LiceyMedio = Enumerador(nombre='Licey al Medio', tipo_enumerador=tipo_de_zona)
        zona_8_LasPalomas = Enumerador(nombre='Las Palomas', tipo_enumerador=tipo_de_zona)
        
        session.add_all([tipo_de_zona,zona_1_Nibaje,zona_2_villa_olimpica,zona_3_cruz_marylopez,
                         zona_4_Pekin,zona_5_CienFuegos,zona_6_Gurabo,zona_7_LiceyMedio,
                         zona_8_LasPalomas])
        
        # Adicinamos los datos en la base de datos
        session.add_all([tipo_de_mora, mora_fija, mora_en_porciento, tipo_de_sucursal,sucursal_1,sucursal_2,sucursal_3])
        
        # Adicionamos los usuarios de tipo administrador 
        u1 = Usuario(nombres="Administrador",apellidos="Prestamos",login_name='admin', password='app2002', rol=rol_admin, sucursal=sucursal_1)
        u2 = Usuario(nombres="Admin Sucursal",apellidos="Prestamos",login_name='admin.sucursal', password='P@ssw0rd2', rol=rol_admin_sucursal, sucursal=sucursal_2)
        u3 = Usuario(nombres="Cobrador",apellidos="Prestamos",login_name='cobrador', password='P@ssw0rd3', rol=rol_cobrador, sucursal=sucursal_3)
        
        
        
        # Adicionamos en la base de datos
        session.add_all([u1, u2, u3])
 
        # Adicionamos una configuracion
        c1 = Configuracion(key=CK.cantidad_maxima_de_creditos_por_cliente, value='18446744073709551616')
        # Salvamos en la base de datos
        session.add_all([c1])

        # Adicionamos los clientes
        client_1 = Cliente(nombres="Jonh",apellidos="Smith",celular="+1 586 984",comentarios="",direccion="",
                           sucursal=sucursal_1,tipo_de_identificacion=identificacion_por_cedula_extranjera,
                           numero_de_identificacion="5222315",telefono="+1 586 984",email="jonh.smith@gmail.com",
                           estado=1,zona=zona_1_Nibaje,owner=u1)
        
        client_2 = Cliente(nombres="James",apellidos="Williams",celular="+1 234 977",comentarios="",direccion="",
                           sucursal=sucursal_2,tipo_de_identificacion=identificacion_por_cedula_extranjera,
                           numero_de_identificacion="5623487",telefono="+1 234 977",email="james.williams@gmail.com",
                           estado=1,zona=zona_2_villa_olimpica,owner=u2)
        
        client_3 = Cliente(nombres="Helen",apellidos="Baker",celular="+1 119 478",comentarios="",direccion="",
                           sucursal=sucursal_3,tipo_de_identificacion=identificacion_por_cedula_extranjera,
                           numero_de_identificacion="5623487",telefono="+1 119 478",email="helen.baker@gmail.com",
                           estado=1,zona=zona_3_cruz_marylopez,owner=u1)
        
        client_4 = Cliente(nombres="jose Marti",apellidos="Perez",celular="+1 119 478",comentarios="",direccion="",
                           sucursal=sucursal_1,tipo_de_identificacion=identificacion_por_cedula_extranjera,
                           numero_de_identificacion="5623487",telefono="+1 119 478",email="jose.marti@gmail.com",
                           estado=1,zona=zona_4_Pekin,owner=u2)
        client_5 = Cliente(nombres="Antonio ",apellidos="Maceo",celular="+1 119 478",comentarios="",direccion="",
                           sucursal=sucursal_2,tipo_de_identificacion=identificacion_por_cedula_extranjera,
                           numero_de_identificacion="5623487",telefono="+1 119 478",email="antonio.maceo@gmail.com",
                           estado=1,zona=zona_5_CienFuegos,owner=u1)
        client_6 = Cliente(nombres="Maximo",apellidos="Gomez Baez",celular="+1 119 478",comentarios="",direccion="",
                           sucursal=sucursal_3,tipo_de_identificacion=identificacion_por_cedula_extranjera,
                           numero_de_identificacion="5623487",telefono="+1 119 478",email="maximo.gomez@gmail.com",
                           estado=1,zona=zona_6_Gurabo,owner=u2)
        client_7 = Cliente(nombres="Carlos Manuel",apellidos="de Cespedez",celular="+1 119 478",comentarios="",direccion="",
                           sucursal=sucursal_3,tipo_de_identificacion=identificacion_por_cedula_extranjera,
                           numero_de_identificacion="5623487",telefono="+1 119 478",email="carlos.manuel@gmail.com",
                           estado=1,zona=zona_7_LiceyMedio,owner=u1)
        
        # Salvamos los clientes en la Base de Datos   
        session.add_all([client_1,client_2,client_3,
                         client_4,client_5,client_6,client_7])

        # creamos un tipo de parametro de exportacion
        p1 = ParamExportacion(codigo='mmm', comentario='',
                              nombre='mmm', obligatorio=True, tipo_dato='str')
        
        # Creamos una exportacion
        exp2 = Exportacion(sql_reporte='select * from user where id=:mmm',
                         codigo='dame', activo=True,
                         comentario='dsf', nombre='dame1',
                         nombre_archivo='no.txt', parametros=[p1])
        
        # Salvamos ParamExportacion y Exportacion en la Base de datos
        session.add_all([p1, exp2])

        param_fecha_inicial = ParamExportacion(codigo='fecha_inicial', comentario='la fecha minima',
                                           nombre='fecha_inicial', obligatorio=True, tipo_dato='date')
        param_fecha_final = ParamExportacion(codigo='fecha_final', comentario='la fecha maxima',
                                            nombre='fecha_final', obligatorio=True, tipo_dato='date')

        exp1 = Exportacion(sql_reporte='select * from cliente where created_at BETWEEN :fecha_inicial AND :fecha_final',
                        codigo='clientes_registrados_en_fecha', activo=True,
                        comentario='Obtiene los clientes registrados entre dos fechas dadas.',
                        nombre='clientes_registrados_en_fecha',
                        nombre_archivo='no.txt', parametros=[param_fecha_inicial, param_fecha_final])
        
        session.add(exp1)
        
        # Adicionamos los creditos
        credito_1 = Credito(comentario="Credito 1",cobrador=u3, creador=u1,tasa_de_interes=10,monto=1000,owner=client_1,
                            fecha_de_aprobacion="2024-06-07",numero_de_cuotas=3,estado=1,dias_adicionales=2,
                            valor_de_mora=5,frecuencia_del_credito=credito_diario, tipo_de_mora=mora_fija,garante=client_1
                            ,sucursal_id=22)
       
        credito_2 = Credito(comentario="Credito 2",cobrador=u3,creador=u2,tasa_de_interes=12,monto=2000,owner=client_1,
                            fecha_de_aprobacion="2024-06-18",numero_de_cuotas=5,estado=1,dias_adicionales=2,
                            valor_de_mora=5,frecuencia_del_credito=credito_diario, tipo_de_mora=mora_fija,garante=client_2
                            ,sucursal_id=23)
        
        credito_3 = Credito(comentario="Credito 3",cobrador=u3,creador=u3,tasa_de_interes=8,monto=3000,owner=client_1,
                            fecha_de_aprobacion="2024-06-01",numero_de_cuotas=4,estado=1,dias_adicionales=2,
                            valor_de_mora=5,frecuencia_del_credito=credito_diario, tipo_de_mora=mora_fija,garante=client_3
                            ,sucursal_id=24)
        
        credito_4 = Credito(comentario="Credito 4",cobrador=u3,creador=u1,tasa_de_interes=15,monto=5000,owner=client_1,
                            fecha_de_aprobacion="2024-06-10",numero_de_cuotas=3,estado=1,dias_adicionales=2,
                            valor_de_mora=5,frecuencia_del_credito=credito_diario, tipo_de_mora=mora_fija,garante=client_1
                            ,sucursal_id=22)
        
        credito_5 = Credito(comentario="Credito 5",cobrador=u3,creador=u2,tasa_de_interes=10,monto=2500,owner=client_1,
                            fecha_de_aprobacion="2024-06-11",numero_de_cuotas=2,estado=1,dias_adicionales=2,
                            valor_de_mora=5,frecuencia_del_credito=credito_diario, tipo_de_mora=mora_fija,garante=client_2
                            ,sucursal_id=23)
        
        credito_6 = Credito(comentario="Credito 6",cobrador=u3,creador=u3,tasa_de_interes=20,monto=8000,owner=client_1,
                            fecha_de_aprobacion="2024-06-22",numero_de_cuotas=4,estado=1,dias_adicionales=2,
                            valor_de_mora=5,frecuencia_del_credito=credito_diario, tipo_de_mora=mora_fija,garante=client_3
                            ,sucursal_id=24)
        
        lst_credits = [credito_1,credito_2,credito_3,credito_4,credito_5,credito_6]
        
        
        #for credit in lst_credits:
        #    credit.calculate_valor_deuda()
        
        session.add_all(lst_credits)
        
        # ----------------------- cuotas para el credito 1 ----------------------------------------------
        cuota_1 = Cuota(numero_de_cuota=1,fecha_de_pago='2024-06-08',fecha_de_aplicacion_de_mora='2024-05-20',credito=credito_1,
                        pagada=False,valor_pagado=0,valor_de_cuota=250,valor_de_mora=120)
        
        cuota_2 = Cuota(numero_de_cuota=2,fecha_de_pago='2024-06-09',fecha_de_aplicacion_de_mora='2024-05-20',credito=credito_1,
                        pagada=False,valor_pagado=0,valor_de_cuota=250,valor_de_mora=140)
        
        cuota_3 = Cuota(numero_de_cuota=3,fecha_de_pago='2024-06-10',fecha_de_aplicacion_de_mora='2024-05-20',credito=credito_1,
                        pagada=False,valor_pagado=0,valor_de_cuota=250,valor_de_mora=100)
        
        cuota_4 = Cuota(numero_de_cuota=4,fecha_de_pago='2024-06-11',fecha_de_aplicacion_de_mora='2024-05-20',credito=credito_1,
                        pagada=False,valor_pagado=0,valor_de_cuota=250,valor_de_mora=170)
        
        lst_cuotas_credit_1:List[Cuota] = [cuota_1,cuota_2,cuota_3,cuota_4]
        session.add_all(lst_cuotas_credit_1)
        
        
        # reportes por usuario
        config_report_by_user_1 = ExportacionByUser(reporte_config=exp1,rol_config=rol_admin,descripcion="Obtener Clientes en un rango de fechas")
        config_report_by_user_2 = ExportacionByUser(reporte_config=exp2,rol_config=rol_admin,descripcion="Obtener Usuarios por un ID Dado")
        
        session.add_all([config_report_by_user_1,config_report_by_user_2])
        
        #--------------------- pagos para las cuotas pagadas del credito #1 --------------------------------------
        
        """
        pago_1 = Pago(comentario="Pago #1 - Credito #1", fecha_de_pago='2024-06-08',
                             valor_del_pago=250,tiene_mora=True,registrado_por_usuario_id=1,credito=credito_1)
        
        pago_2 = Pago(comentario="Pago #2 - Credito #1", fecha_de_pago='2024-06-09',
                             valor_del_pago=250,tiene_mora=False,registrado_por_usuario_id=1,credito=credito_1)
        
        pago_3 = Pago(comentario="Pago #3 - Credito #1", fecha_de_pago='2024-06-09',
                             valor_del_pago=250,tiene_mora=True,registrado_por_usuario_id=1,credito=credito_1)
        
         
        lst_pagos:List[PagoDeCuota] = [pago_1,pago_2,pago_3]
        
        session.add_all(lst_pagos)
        
        
        #--------------------- comprobantes de pago para los pagos --------------------------------------------
        
        cmp_pago_1 = ComprobanteDePago(pago=pago_1,nombre_del_cliente=client_1.nombres,
                                       cedula="5112-12132", telefono=client_1.telefono,pendiente=0,comentario="Test 1")
        
        cmp_pago_2 = ComprobanteDePago(pago=pago_2,nombre_del_cliente=client_2.nombres,
                                       cedula="5112-12132", telefono=client_2.telefono,pendiente=0, comentario="test 2")
        
        cmp_pago_3 = ComprobanteDePago(pago=pago_3,nombre_del_cliente=client_3.nombres,
                                       cedula="5112-12132", telefono=client_3.telefono,pendiente=0, comentario="test 3")
        
        session.add_all([cmp_pago_1,cmp_pago_2,cmp_pago_3])
        """
        
        # Salvamos todos los cambios en la BD
        session.commit()

print("Log: Datos Insertados con exito")
