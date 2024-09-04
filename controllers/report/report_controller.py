import pandas as pd
import sys, os
from controllers.report.base.abono_credit_interest import AbonoCreditInterestReport
import pdfkit
# import calendar
# import datetime

from controllers.report.base.client_credit import ClientCreditReport
from controllers.report.base.recaudo import RecaudoReport
from controllers.report.base.deuda_by_client import DeudaByClientReport
from controllers.report.base.cartera import CarteraReport

# path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
# config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
options = {
    'footer-right': '[page] of [topage]'
    } 




path_linux_local = "/home/ubuntu/project/front/deudas-morosas/build/"
path_windows_local = "C:/laragon/www/api/backend/"
client_credit_report = ClientCreditReport()
recaudo_report = RecaudoReport()
deuda_by_client = DeudaByClientReport()
cartera_report = CarteraReport()
abono_credito_interes = AbonoCreditInterestReport()
# from threading import Thread

class ReportController:

    def __init__(self, db:any) -> None:
        self.db = db

    # TODO: Reporte para traer pagos de x fecha a x fecha con informacion de credito y clientes
    def report_payment_by_day(self, data: dict) -> str:
        offset = 30
        calculate = int(data['offset'])*offset
        calculate = calculate - offset
        if int(data['offset']) == 0 or int(data['offset']) == 1:
            calculate = 0
        query = f"""
            select p.id as id_pago, p.way_to_pay as forma_pago, p.code_transaction as transaccion, 
            p.description, p.value as valor_pago, p.start_payment_at as fecha_pago,
            (select concat(u.first_name, ' ', u.last_name) from Usuarios u where u.id = p.created_by) as pago_credo_por,
            (select concat(u.first_name, ' ', u.last_name) from Usuarios u where u.id = p.updated_by) as pago_actualizado_por,
            c.value as credito_valor_inicial, c.utility as credito_valor_final, c.value_paid as credito_pagado,
            c.quota as numero_de_cuotas, c.code2 as credito_codigo, c.start_credit_at as credito_fecha_aprobado, c."comment" as credito_comentario,
            concat(c2.first_name, ' ', c2.last_name) as cliente_nombres, c2.type_identification as cliente_tipo_identificacion, c2.number_identification as cliente_numero_identificacion,
            c2.phone as cliente_celular, c2.address as cliente_direccion, c2.alias as cliente_alias
            ,(
                select sum(p3.value::float)
                from payments p3 
                where p3.id_credit =c.id
                and to_timestamp(p3.start_payment_at, 'YYYY-MM-DD')::timestamp >= concat('{data['start_date']}',' ','00:00:00')::timestamp and to_timestamp(p3.start_payment_at, 'YYYY-MM-DD')::timestamp <= concat('{data['end_date']}',' ','23:59:59')::timestamp
                and p3.state ='1'
            )as total_credito_acumulado
            ,(
                select sum(p2.value::float) 
                from payments p2
                inner join credits c3 on c3.id = p2.id_credit 
                inner join clients c4 on c4.id = c3.id_client 
                where to_timestamp(p2.start_payment_at, 'YYYY-MM-DD')::timestamp >= concat('{data['start_date']}',' ','00:00:00')::timestamp and to_timestamp(p2.start_payment_at, 'YYYY-MM-DD')::timestamp <= concat('{data['end_date']}',' ','23:59:59')::timestamp
                and p2.state ='1'
                and c3.state ='1'
                and c4.state ='1'
                """
        if data['client_id'] != "":
            query += f""" and c4.id='{data['client_id']}' """
        
        query += f""") as total_recibir
            from payments p
            inner join credits c on c.id = p.id_credit
            inner join clients c2 on c2.id = c.id_client 
            where to_timestamp(p.start_payment_at, 'YYYY-MM-DD')::timestamp >= concat('{data['start_date']}',' ','00:00:00')::timestamp and to_timestamp(p.start_payment_at, 'YYYY-MM-DD')::timestamp <= concat('{data['end_date']}',' ','23:59:59')::timestamp
            and p.state = '1'
            and c.state = '1'
            and c2.state='1'
            """
        if data['client_id'] != "":
            query += f" and c2.id ='{data['client_id']}'"
        query += f" order by c2.first_name; ";
        # query += f"""order by c2.id 
        #     limit '{data['limit']}'
        #     offset '{calculate}';
        # """
        return query
    # TODO: reporte para traer clientes que creditos deben con su informacion
    def report_client_credit(self, data: dict) -> str:
        offset = 30
        calculate = int(data['offset'])*offset
        calculate = calculate - offset
        if int(data['offset']) == 0 or int(data['offset']) == 1:
            calculate = 0
        query = f"""
            select 
            c.value as credito_valor_inicial, c.utility as credito_valor_final, c.value_paid as credito_pagado,
            c.quota as numero_de_cuotas, c.code as credito_codigo, c.start_credit_at as credito_fecha_aprobado, c."comment" as credito_comentario,
            concat(c2.first_name, ' ', c2.last_name) as cliente_nombres, c2.type_identification as cliente_tipo_identificacion, c2.number_identification as cliente_numero_identificacion,
            c2.phone as cliente_celular, c2.address as cliente_direccion, c2.alias as cliente_alias
            from clients as c2
            inner join credits c on c.id_client = c2.id
            where to_timestamp(cast(c2.created_at as TEXT) , 'YYYY-MM-DD HH24:MI:SS')::timestamp >= '{data['start_date']}' and to_timestamp(cast(c2.created_at as TEXT), 'YYYY-MM-DD HH24:MI:SS')::timestamp <= '{data['end_date']}'
            and c.state = '1'
            and c2.state = '1'
            """
        if data['client_id'] != "":
            query += f" and c2.id ='{data['client_id']}' "
        query += f"""order by c2.id 
            limit '{data['limit']}'
            offset '{calculate}';
        """
        return query    
    # TODO: reporte para traer cuanto se ha prestado, pagado y a ganar al final, reporte de cartera
    def report_credit_cartera(self) -> str:
        # query = f"""
        #     select sum(c.value::float) as prestado, sum(c.value_paid::float) as pagado, (sum(c.utility::float) - sum(c.value::float)) as ganancias_finales, join_ganado_actual.ganado_actual
        #     from clients as c2
        #     inner join credits c on c.id_client = c2.id
        #     left join (select (sum(value_paid::float) - sum(value::float)) as ganado_actual
        #         from clients c2
        #         inner join credits c on c.id_client = c2.id
        #         where c.state ='1'
        #         and c2.state = '1'
        #         and value_paid::float > value::float) as join_ganado_actual on true
        #     where c.state ='1'
        #     and c2.state = '1'
        #     and to_timestamp(cast(c.start_credit_at as TEXT) , 'YYYY-MM-DD HH24:MI:SS')::timestamp >= '{data['start_date']}' and to_timestamp(cast(c.start_credit_at as TEXT), 'YYYY-MM-DD HH24:MI:SS')::timestamp <= '{data['end_date']}'
        #     group by join_ganado_actual.ganado_actual;
        # """
        query = f""" 
            select *, 
            (todo.prestado::float+todo.intereses::float) as total_prestamo, --nuevo
            (todo.prestado::float+todo.intereses::float - todo.total_pagado::float) as saldo_pendiente, --nuevo
            (todo.fecha_inicio::timestamp + cast(todo.total_cuotas || ' days' as interval) )as finaliza_credito --nuevo
            from (
                select c.id as id_client, c2.id as id_credit, c.first_name, concat(c.first_name,' ', c.last_name),
                (c2.code2) as nombre_credito, --nuevo
                (c2.start_credit_at) as fecha_inicio, --nuevo
                (c2.way_to_pay) as forma_de_pago, --nuevo
                sum(c2.value::float) as prestado, (c2.utility::float - c2.value::float) as intereses,
                (c2.value_paid) as total_pagado,
                (c2.value_paid::float -(((c2.utility::float - c2.value::float)/c2.quota)*(select count(p.id) from payments p where p.id_credit=c2.id)::float)) as capital_pagado,
                (((c2.utility::float - c2.value::float)/c2.quota)*(select count(p.id) from payments p where p.id_credit=c2.id)::float) as interes_pagado,
                (c2.utility::float - c2.value_paid::float) as saldo_pendiente,
                (((c2.utility::float-c2.value::float)/c2.quota)*(c2.quota::float - (select count(p.id) from payments p where p.id_credit=c2.id)::float)) as interes_pendiente,
                ((c2.utility::float-c2.value_paid::float)-(((c2.utility::float-c2.value::float)/c2.quota)*(c2.quota::float - (select count(p.id) from payments p where p.id_credit=c2.id)::float))) as capital_pendiente,
                (c2.quota) as total_cuotas, (select count(p.id) from payments p where p.id_credit=c2.id)::float as cuotas_pagas,
                (c2.quota::float - (select count(p.id) from payments p where p.id_credit=c2.id)::float) as cuotas_pendientes,
                ( 
                    case when (split_part((
                    ((c2.start_credit_at::timestamp + cast(c2.quota || ' days' as interval)) - c2.start_credit_at)-cast ((select count(p.id) from payments p where p.id_credit=c2.id and p.state='1') || ' days' as interval)
                    )::text, ' ', 1) 
                    )='00:00:00' then('0') else (
                    split_part((
                    ((c2.start_credit_at::timestamp + cast(c2.quota || ' days' as interval)) - c2.start_credit_at)-cast ((select count(p.id) from payments p where p.id_credit=c2.id and p.state='1') || ' days' as interval)
                    )::text, ' ', 1) 
                    ) end
                ) as cuotas_mora,
                (c2.utility::float/c2.quota::float) as valor_cuota --nuevo
                from clients c 
                inner join credits c2 on c2.id_client =c.id 
                where c.state ='1'
                and c2.state ='1'
                and c2.value_paid::float < c2.utility::float
                group by c.first_name, c.last_name, c2.utility, c2.value, c2.id, c.id
            ) as todo
            --where todo.cuotas_mora::float > 0
            order by todo.first_name;
        """
        return query
    
    # TODO: reporte por cliente por credito
    def report_client_credit(self, data: dict) -> str:
        """ 
            select row_number() OVER () AS consecutivo, *, p.value as pago_valor, (select sum(value::float) from payments p2 where p2.id_credit=c.id) as total_pagos, (select count(id) from payments p3 where p3.id_credit=c.id) as total_cuotas_pagas
        """
        query = f"""
        select row_number() OVER () AS consecutivo, *, p.value as pago_valor,(select sum(value::float) from payments p2 where p2.id_credit=c.id and p2.state='1') as total_pagos, ((select sum(value::float) from payments p2 where p2.id_credit=c.id and p2.state='1')::float / ((c.utility::float/c.quota::float))::float) as total_cuotas_pagas--(select count(id) from payments p3 where p3.id_credit=c.id and p3.state='1') as total_cuotas_pagas
            , concat(u.first_name, ' ', u.last_name) as update_by_Usuario
            , c2.address as client_address
            , c2.first_name as first_name, c2.last_name as last_name
            , c2.phone as celular, c2.number_identification as number_identification
            from payments p 
            inner join credits c on c.id = p.id_credit 
            inner join clients c2 on c2.id = c.id_client
            left join Usuarios u on u.id = p.updated_by 
            where c2.id ='{data['client_id']}'
            and c.id='{data['credit_id']}'
            and to_timestamp(cast(c.start_credit_at as TEXT) , 'YYYY-MM-DD HH24:MI:SS')::timestamp >= '{data['start_date']}' and to_timestamp(cast(c.start_credit_at as TEXT), 'YYYY-MM-DD HH24:MI:SS')::timestamp <= '{data['end_date']}'
            order by c.id asc
        """
        return query

    # TODO: reporte por cuotas pendientes
    def report_quote_not_payment(self, data: dict) -> str:
        query = f"""
            select *, split_part(todo2.diferencia_deuda::text, ' ', 1) as total_dia_mora, split_part(todo2.cuotas_pagas::text, ' ', 1) as total_cuotas_pagas, todo2.finaliza_credito
            from (
                select todo.*, (todo.dias_diferencia - cuotas_pagas) as diferencia_deuda, (todo.start_credit_at::timestamp + cast(todo.quota || ' days' as interval) )as finaliza_credito
                from (
                    select *
                    , cast ((select count(p.id) from payments p where p.id_credit=c.id) || ' days' as interval) as cuotas_pagas
                    , ((c.start_credit_at::timestamp + cast(c.quota || ' days' as interval)) - c.start_credit_at)as dias_diferencia
                    , (
                        select p.start_payment_at 
                        from payments p 
                        where p.id_credit = c.id 
                        order by p.start_payment_at desc limit 1
                    ) as ultimo_pago
                    from credits c
                    where c.value_paid::float < c.utility::float
                ) as todo
                where todo.ultimo_pago::timestamp < (current_timestamp - interval '1 days') 
                )
            as todo2
            inner join clients c2 on c2.id  = todo2.id_client
            where todo2.diferencia_deuda > cast(1 || ' days' as interval)
            and (todo2.finaliza_credito - interval ' 1 days') < (todo2.ultimo_pago::timestamp)
            order by todo2.diferencia_deuda desc;
        """
        return query
    
    # TODO: reporte por dia porcentaje de abono credito y porcentaje abono intereses
    def report_porcent_credit_interest(self, data: dict) -> str:
        # query = f"""
        #     select sum(p.value::float) as total, sum(p.value::float*0.83) as credit, sum(p.value::float*0.17) as intereses
        #     from payments p 
        #     inner join credits c on c.id = p.id_credit 
        #     inner join clients c2 on c2.id  = c.id_client 
        #     where p.start_payment_at::timestamp >= concat('{data['start_date']}',' ','00:00:00')::timestamp
        #     and p.start_payment_at::timestamp <=  concat('{data['end_date']}',' ','23:59:59')::timestamp
        #     and c.state ='1'
        #     and c2.state ='1'
        #     and p.state ='1';
        # """
        query = f"""
            select  sum(p.value::float) as total_recibir, 
            sum(p.value::float*0.83) as credit_payment, sum(p.value::float*0.17) as intereses_payment,
            (
                select sum(c.value::float)
                from credits c
                inner join clients c2 on c2.id = c.id_client 
                where c.state ='1'
                and c2.state ='1'
            ) as prestado_a_clientes,
            (
                select sum(c.value_paid::float)
                from credits c
                inner join clients c2 on c2.id = c.id_client 
                where c.state ='1'
                and c2.state ='1'
            ) as pagado_por_clientes,
            (
                select sum(c.value_paid::float*0.83)
                from credits c
                inner join clients c2 on c2.id = c.id_client 
                where c.state ='1'
                and c2.state ='1'
            ) as credit_value, (
                select sum(c.value_paid::float*0.17)
                from credits c
                inner join clients c2 on c2.id = c.id_client 
                where c.state ='1'
                and c2.state ='1'
            ) as intereses_value
            from payments p 
            inner join credits c on c.id = p.id_credit 
            inner join clients c2 on c2.id  = c.id_client 
            where p.start_payment_at::timestamp >= concat('{data['start_date']}',' ','00:00:00')::timestamp
            and p.start_payment_at::timestamp <=  concat('{data['end_date']}',' ','23:59:59')::timestamp
            and c.state ='1'
            and c2.state ='1'
            and p.state ='1'
            limit 1;
        """
        return query

    def get_report(self, data:dict)-> dict:
        try:
            # Start Transaction
            conn = self.db.connect_db()

            query = ""
            name_file = ""
            report_type = None
            if data['id'] == "1" or data['id'] == 1:
                query = self.report_payment_by_day(data)
                name_file = "recaudo_por_fecha.pdf"
                query = self.db.transaction(
                    query,
                    conn)
                cursor = query[1]
                get_query = query[0]
                if len(get_query) ==0:
                    return {"status": 202, "data": ""}
                report_type = recaudo_report.html_report(get_query)
                try:
                    # pdfkit.from_string(report_type, path_windows_local+name_file, configuration=config)
                    pdfkit.from_string(report_type, path_linux_local+name_file)
                except:
                    pass
            elif data['id'] == "2" or data['id'] == 2:
                query = self.report_client_credit(data)
            elif data['id'] == "3" or data['id'] == 3:
                query = self.report_credit_cartera()
                name_file = "cartera.pdf"
                query = self.db.transaction(
                    query,
                    conn)
                cursor = query[1]
                get_query = query[0]
                if len(get_query) ==0:
                    return {"status": 202, "data": ""}
                # cartera_report.html_report(get_query, path_windows_local+name_file)
                cartera_report.html_report(get_query, path_linux_local+name_file)
                # pdfkit.from_string(report_type, path_windows_local+name_file, configuration=config, options=options)
                # pdfkit.from_string(report_type, path_linux_local+name_file,options=options)
            elif data['id'] == "4" or data['id'] == 4:
                query = self.report_client_credit(data)
                print(query)
                name_file = "cliente_credito.pdf"
                query = self.db.transaction(
                    query,
                    conn)
                cursor = query[1]
                get_query = query[0]
                if len(get_query) ==0:
                    return {"status": 202, "data": ""}
                report_type = client_credit_report.html_report(get_query)
                # pdfkit.from_string(report_type, path_windows_local+name_file, configuration=config)
                pdfkit.from_string(report_type, path_linux_local+name_file)
            elif data['id'] == "5" or data['id'] == 5:
                query = self.report_quote_not_payment(data)
                name_file = "reporte_cliente_mora.pdf"
                query = self.db.transaction(
                    query,
                    conn)
                cursor = query[1]
                get_query = query[0]
                if len(get_query) ==0:
                    return {"status": 202, "data": ""}
                report_type = deuda_by_client.html_report(get_query)
                # pdfkit.from_string(report_type, path_windows_local+name_file, configuration=config)
                pdfkit.from_string(report_type, path_linux_local+name_file)
            elif data['id'] == "6" or data['id'] == 6: #reporte diario creditos con intereses
                query = self.report_porcent_credit_interest(data)
                name_file = "reporte_abono_credito_interes.pdf"
                query = self.db.transaction(
                    query,
                    conn)
                cursor = query[1]
                get_query = query[0]
                if len(get_query) ==0:
                    return {"status": 202, "data": ""}
                report_type = abono_credito_interes.html_report(get_query)
                # pdfkit.from_string(report_type, path_windows_local+name_file, configuration=config)
                pdfkit.from_string(report_type, path_linux_local+name_file)
            self.db.transaction_close(conn, cursor)
            return {"status": 200, "data": name_file}
            # Finish Transaction
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.db.execute_one(f"""
                insert into logs(code, file, function_failed, description)
                values ('500', 'report_controller.py', 'get_report', '{str(e).replace("'", "")+ " " +str(fname)+" "+str(exc_tb.tb_lineno)}') returning id;
            """)
            return {"status": 500, "data": {}}
