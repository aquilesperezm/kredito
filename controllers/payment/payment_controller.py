from functions.generate_string import GenerateString
import sys, os

generate_string = GenerateString()

class PaymentController:

    def __init__(self, db:any) -> None:
        self.db = db

    def new_payment(self, data:dict) -> dict:
        try:
            # Start Transaction
            conn = self.db.connect_db()
            total = int(data['total_payment']) * int(data['value_payment'])
            for index, payment in enumerate(range(int(data['total_payment']))):
                new_quota = self.db.transaction(f"""
                    insert into payments (owner_Usuario_id, id_credit, way_to_pay, code_transaction, description, value, created_by, start_payment_at, updated_by)
                    values('{data['Usuario_id']}', '{data['credit_id']}', '{data['way_to_pay']}', '{generate_string.generate()}', '{data['comment_payment']}', '{data['value_payment']}', '{data['created_by']}', '{data['start_payment_at']}', '{data['created_by']}') returning *;
                """,
                conn);
                cursor = new_quota[1]
                get_quota = new_quota[0]
            get_credit_paid = self.db.transaction_execute(f"""
                select *
                from credits c 
                where id='{data['credit_id']}';
            """,
            cursor,
            conn);
            cursor = get_credit_paid[1]
            get_credit = get_credit_paid[0]
            sum_total_credit_paid = int(total)+int(get_credit[0]['value_paid'])
            update_credit_paid = self.db.transaction_execute(f"""
                update credits
                set value_paid = '{sum_total_credit_paid}'
                where id='{data['credit_id']}' returning *;
            """,
            cursor,
            conn);
            cursor = update_credit_paid[1]
            get_credit = update_credit_paid[0]
            self.db.transaction_close(conn, cursor)
            # Finish Transaction
            return {"status": 200}
        except Exception as e:
            self.db.execute_one(f"""
                insert into logs(code, file, function_failed, description)
                values ('500', 'payment_controller.py', 'new_payment', '{str(e).replace("'", "")}') returning id;
            """)
            return {"status": 500, "data": {}}

    def get_all_payment(self, data:dict) -> dict:
        try:
            offset = 20
            calculate = int(data['page'])*offset
            calculate = calculate - offset
            if int(data['page']) == 0 or int(data['page']) == 1:
                calculate = 0
            # Start Transaction
            conn = self.db.connect_db()
            query_payments = self.db.transaction(f"""
                select p.id as payment_id, c2.number_identification as client_number_identification, c2.first_name as client_first_name, c2.last_name as client_last_name, u.first_name as Usuario_first_name, u.last_name as Usuario_last_name, p.value as payment_value, p.updated_by as payment_updated_by,p.id as payment_id,*, count(p.id) over() as total
                , c.code2 as code2
                from payments p
                inner join credits c on c.id = p.id_credit 
                inner join clients c2 on c2.id = c.id_client
                left join Usuarios u on u.id = p.updated_by
                where p.owner_Usuario_id ='{data['Usuario_id']}'
                and p.state ='1'
                order by p.start_payment_at desc
                limit 20 offset {calculate};
            """,
            conn)
            cursor = query_payments[1]
            get_payments = query_payments[0]
            if len(get_payments) ==0:
                total_rows = 0
            else:
                total_rows = get_payments[0]['total']
            self.db.transaction_close(conn, cursor)
            # Finish Transaction
            return {"status": 200, "total": total_rows, "payments": get_payments}
        except Exception as e:
            self.db.execute_one(f"""
                insert into logs(code, file, function_failed, description)
                values ('500', 'payment_controller.py', 'get_all_payment', '{str(e).replace("'", "")}') returning id;
            """)
            return {"status": 500, "data": {}}
    
    def get_by_id(self, id:dict) -> dict:
        try:
            # Start Transaction
            conn = self.db.connect_db()
            query_payment = self.db.transaction(f"""
                select p.value as payment_value, * 
                from payments p
                inner join credits c on c.id = p.id_credit 
                inner join clients c2 on c2.id = c.id_client
                where p.id='{id['id']}';
            """,
            conn)
            cursor = query_payment[1]
            get_payment = query_payment[0]
            self.db.transaction_close(conn, cursor)
            # Finish Transaction
            return {"status": 200, "data": get_payment}
        except Exception as e:
            self.db.execute_one(f"""
                insert into logs(code, file, function_failed, description)
                values ('500', 'payment_controller.py', 'get_by_id', '{str(e).replace("'", "")}') returning id;
            """)
            return {"status": 500, "data": {}}

    def modify_payment(self, data:dict) -> dict:
        try:
             # Start Transaction
            conn = self.db.connect_db()
            
            get_credit_paid = self.db.transaction(f"""
                select p.value as payment_value, c.id as credit_id,* 
                from payments p 
                inner join credits c on c.id = p.id_credit 
                where p.id ='{data['id']}';
            """,
            conn);
            cursor = get_credit_paid[1]
            get_credit = get_credit_paid[0]

            before_modify_payment_value = int(float(get_credit[0]['payment_value']))
            new_modify_payment_value = int(float(data['value_payment']))
            credit_value_paid = int(float(get_credit[0]['value_paid']))
            diference_update_value_credit = 0
            new_credit_value_paid = 0
            if credit_value_paid > 0:
                if before_modify_payment_value > new_modify_payment_value:
                    diference_update_value_credit = before_modify_payment_value - new_modify_payment_value
                    new_credit_value_paid = credit_value_paid - diference_update_value_credit
                elif before_modify_payment_value < new_modify_payment_value:
                    diference_update_value_credit = new_modify_payment_value - before_modify_payment_value
                    new_credit_value_paid = credit_value_paid + diference_update_value_credit

                if new_credit_value_paid > 0:
                    query_update_credit_value_paid = self.db.transaction_execute(f"""
                        update credits
                        set value_paid = '{new_credit_value_paid}'
                        where id='{get_credit[0]['credit_id']}' returning *;
                    """,
                    cursor,
                    conn)
                    cursor = query_update_credit_value_paid[1]
                    get_updated_credit_value_paid = query_update_credit_value_paid[0]

            query_payment = self.db.transaction_execute(f"""
                update payments 
                set way_to_pay = '{data['way_to_pay']}',
                description = '{data['description']}',
                value ='{data['value_payment']}',
                start_payment_at = '{data['start_payment_at']}',
                updated_by = '{data['updated_by']}',
                updated_at = CURRENT_TIMESTAMP
                where id='{data['id']}' returning *;
            """,
            cursor,
            conn)
            cursor = query_payment[1]
            get_payment = query_payment[0]
            self.db.transaction_close(conn, cursor)
            # Finish Transaction
            return {"status": 200}
        except Exception as e:
            self.db.execute_one(f"""
                insert into logs(code, file, function_failed, description)
                values ('500', 'payment_controller.py', 'modify_payment', '{str(e).replace("'", "")}') returning id;
            """)
            return {"status": 500, "data": {}}

    def find_by_name_email_identification(self, data: dict) -> dict:
        try:
            offset = 20
            calculate = int(data['page'])*offset
            calculate = calculate - offset
            if int(data['page']) == 0 or int(data['page']) == 1:
                calculate = 0
            # Start Transaction
            conn = self.db.connect_db()
            find_client = self.db.transaction(f"""
                select c.number_identification as client_number_identification, c.first_name as client_first_name, 
                c.last_name as client_last_name, u.first_name as Usuario_first_name, u.last_name as Usuario_last_name, 
                p.value as payment_value, p.updated_by as payment_updated_by,p.id as payment_id,*, count(*) over() as total
                from clients as c
                inner join credits c2 on c2.id_client = c.id
                inner join payments p on p.id_credit = c2.id 
                left join Usuarios u on u.id = p.updated_by
                where ((concat(c.first_name::text , ' ' , c.last_name::text) like '%{data['data'].replace(' ', '%')}%'))
                or (c.email like '%{data['data']}%'
                or c.first_name like '%{data['data']}%'
                or c.last_name like '%{data['data']}%'
                or c.number_identification like '%{data['data']}%')
                or p.code_transaction like '%{data['data']}%'
                and c.id in (
                        select client_id from Usuarios_clients uc where uc.Usuario_id ='{data['id']}'
                    ) 
                and c.state = 1
                and c2.state ='1'
                and c2.owner_Usuario_id ='{data['id']}'
                limit 20 offset {calculate};
                """,
                conn);
            cursor = find_client[1]
            client = find_client[0]
            if len(client) ==0:
                total_rows = 0
            else:
                total_rows = client[0]['total']                
            self.db.transaction_close(conn, cursor)
            # Finish Transaction
            return{"status": 200, "total": total_rows, "data": client}
        except Exception as e:
            self.db.execute_one(f"""
                insert into logs(code, file, function_failed, description)
                values ('500', 'payment_controller.py', 'find_by_name_email_identification', '{str(e).replace("'", "")}') returning id;
            """)
            return {"status": 500, "data": {}}

    def delete_payment_id(self, data:dict)->dict:
        try:
            crude_data = str(data['id'])
            replace_data = crude_data.replace('[', '(')
            replace_data = replace_data.replace(']', ')')
            replace_data = replace_data.replace('"', '\'')
            # Start Transaction
            conn = self.db.connect_db()
            get_payment = self.db.transaction(f"""
                select *
                from payments p 
                where id in {replace_data};
                """,
                conn);
            cursor = get_payment[1]
            payment = get_payment[0]
            for index, temp_data in enumerate(payment):
                update_credit = self.db.transaction_execute(f"""
                    update credits 
                    set value_paid = (
                        select value_paid 
                        from credits c 
                        where c.id ='{temp_data['id_credit']}')::float - '{temp_data['value']}'::float
                    where id ='{temp_data['id_credit']}' returning *;
                """,
                cursor,
                conn)
                cursor = update_credit[1]
                get_credit = update_credit[0]
                delete_payment = self.db.transaction_execute(f"""
                    delete from payments as p 
                    where p.id in ('{temp_data['id']}') returning *;
                """,
                cursor,
                conn)
                cursor = delete_payment[1]
                get_credit = delete_payment[0]
            self.db.transaction_close(conn, cursor)
            # Finish Transaction
            return {"status": 200, "data": {}}
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.db.execute_one(f"""
                insert into logs(code, file, function_failed, description)
                values ('500', 'payment_controller.py', 'delete_payment_id', '{str(e).replace("'", "")+ " " +str(fname)+" "+str(exc_tb.tb_lineno)}') returning id;
            """)
            return {"status": 500, "data": {}}

    def empty_by_credit(self, data:dict) -> dict:
        try:
            # Start Transaction
            conn = self.db.connect_db()
            query_payment = self.db.transaction(f"""
                delete from payments 
                where id_credit ='{data['id']}' returning *;
            """,
            conn)
            cursor = query_payment[1]
            get_payment = query_payment[0]
            update_credit = self.db.transaction_execute(f"""
                    update credits 
                    set value_paid = '0'
                    where id ='{data['id']}' returning *;
                """,
                cursor,
                conn)
            cursor = update_credit[1]
            get_credit = update_credit[0]
            self.db.transaction_close(conn, cursor)
            # Finish Transaction
            return {"status": 200, "data": {}}
        except Exception as e:
            self.db.execute_one(f"""
                insert into logs(code, file, function_failed, description)
                values ('500', 'payment_controller.py', 'empty_by_credit', '{str(e).replace("'", "")}') returning id;
            """)
            return {"status": 500, "data": {}}