import enum
from functions.generate_string import GenerateString
import os, sys

generate_string = GenerateString()

class CreditController:

    def __init__(self, db:any) -> None:
        self.db = db
    
    def new_credit(self, data:dict):
        try:
            conn = self.db.connect_db()
            search_credits = self.db.transaction(f"""
                select *
                from credits c 
                inner join clients c2 on c2.id = c.id_client 
                where c.id_client ='{data['id_client']}'
                order by c.id desc
                limit 1;
            """,
            conn)
            cursor = search_credits[1]
            get_credits = search_credits[0]
            first_name = ""
            last_name = ""
            counter = 1
            if len(get_credits) > 0:
                if get_credits[0]['first_name'][0] == " ":
                        get_credits[0]['first_name'] = get_credits[0]['first_name'][1:]
                if get_credits[0]['last_name'][0] == " ":
                    get_credits[0]['last_name'] = get_credits[0]['last_name'][1:]
                first_name = get_credits[0]['first_name'].split(' ')
                last_name = get_credits[0]['last_name'].split(' ')
                if " " in get_credits[0]['first_name']:
                    first_name = first_name[0]
                else:
                    first_name = get_credits[0]['first_name']
                if " " in get_credits[0]['last_name']:
                    last_name = last_name[0]
                else:
                    last_name = get_credits[0]['last_name']
                last_number_code= get_credits[0]['code2'].split('-')
                counter = int(last_number_code[1])+1
            else:
                query_client = self.db.transaction_execute(f"""
                    select *
                    from clients c 
                    where id ='{data['id_client']}';
                """,
                cursor,
                conn);
                cursor = query_client[1]
                get_client = query_client[0]
                if get_client[0]['first_name'][0] == " ":
                        get_client[0]['first_name'] = get_client[0]['first_name'][1:]
                if get_client[0]['last_name'][0] == " ":
                    get_client[0]['last_name'] = get_client[0]['last_name'][1:]
                first_name = get_client[0]['first_name'].split(' ')
                last_name = get_client[0]['last_name'].split(' ')
                if " " in get_client[0]['first_name']:
                    first_name = first_name[0]
                else:
                    first_name = get_client[0]['first_name']
                if " " in get_client[0]['last_name']:
                    last_name = last_name[0]
                else:
                    last_name = get_client[0]['last_name']
            search_interest = self.db.transaction_execute(f"""
                select *
                from interests i 
                where value ='{round(float(data['porcent']), 2)}'
                order by id desc;
            """,
            cursor,
            conn)
            cursor = search_interest[1]
            get_interest = search_interest[0]
            if len(get_interest)<1:
                search_interest = self.db.transaction_execute(f"""
                    insert into interests (value)
                    values('{round(float(data['porcent']), 2)}') returning *;
                """,
                cursor,
                conn)
                cursor = search_interest[1]
                get_interest = search_interest[0]
            new_credit = self.db.transaction_execute(f"""
                insert into credits (id_client, owner_Usuario_id, value, quota, utility, id_interest, code, comment, start_credit_at, state, code2)
                values ('{data['id_client']}', '{data['Usuario_id']}', '{data['value']}', '{data['quota']}', '{data['utility']}', '{get_interest[0]['id']}', '{generate_string.generate()}', '{data['comment']}','{data['start_credit_at']}', '{data['state']}', '{first_name}{last_name}-{counter}') returning *;
            """,
            cursor,
            conn)
            cursor = new_credit[1]
            get_credit = new_credit[0]
            self.db.transaction_close(conn, cursor)
            # Finish Transaction
            return {"status": 200}
        except Exception as e:
            self.db.execute_one(f"""
                insert into logs(code, file, function_failed, description)
                values ('500', 'credit_controller.py', 'new_credit', '{str(e).replace("'", "")}') returning id;
            """)
            return {"status": 500, "data": {}}
    
    def get_interests(self)->dict:
        try:
            # Start Transaction
            conn = self.db.connect_db()
            query_interest = self.db.transaction(f"""
                select * from interests i2 ;
            """,
            conn)
            cursor = query_interest[1]
            get_interest = query_interest[0]
            self.db.transaction_close(conn, cursor)
            # Finish Transaction
            return {"status": 200, "data": get_interest}
        except Exception as e:
            self.db.execute_one(f"""
                insert into logs(code, file, function_failed, description)
                values ('500', 'credit_controller.py', 'get_interest', '{str(e).replace("'", "")}') returning id;
            """)
            return {"status": 500, "data": {}}
    
    def get_credits(self, data:dict) -> dict:
        try:
            offset = 20
            calculate = int(data['page'])*offset
            calculate = calculate - offset
            if int(data['page']) == 0 or int(data['page']) == 1:
                calculate = 0
            # Start Transaction
            state = '1'
            if data['state'] == "active":
                state = '1'
            elif data['state'] == 'inactive':
                state = '0'
            conn = self.db.connect_db()
            query = f"""
                select *, count(c.id) over() as total,(select count(id) from payments p where c2.id=p.id_credit) as quote_paid
                ,(c2.utility::float/c2.quota) as value_quote
                from clients c
                inner join credits c2 on c2.id_client = c.id 
                where c2.owner_Usuario_id ='{data['Usuario_id']}'
                """
            if data['state'] != 'all' and data['state'] != 'mora':
                query += f"""
                    and c2.state = '{state}'
                """
            elif data['state'] == 'mora':
                query += f"""
                    and c2.id in (
                        select mora.id
						from (
							select *, ( 
                                case when (split_part((
                                ((c2.start_credit_at::timestamp + cast(c2.quota || ' days' as interval)) - c2.start_credit_at)-cast ((select count(p.id) from payments p where p.id_credit=c2.id and p.state='1') || ' days' as interval)
                                )::text, ' ', 1) 
                                )='00:00:00' then('0') else (
                                split_part((
                                ((c2.start_credit_at::timestamp + cast(c2.quota || ' days' as interval)) - c2.start_credit_at)-cast ((select count(p.id) from payments p where p.id_credit=c2.id and p.state='1') || ' days' as interval)
                                )::text, ' ', 1) 
                                ) end
                            ) as cuotas_mora
							from credits as c2
						) as mora
						where mora.cuotas_mora::float >0
                    )
                """
            query += f"""
                order by c2.start_credit_at desc
                limit 20 offset {calculate};
            """
            query_credits = self.db.transaction(
                query,
                conn)
            cursor = query_credits[1]
            get_credits = query_credits[0]
            if len(get_credits) ==0:
                total_rows = 0
            else:
                total_rows = get_credits[0]['total']
            self.db.transaction_close(conn, cursor)
            # Finish Transaction
            return {"status": 200, "total": total_rows, "credits": get_credits}
        except Exception as e:
            self.db.execute_one(f"""
                insert into logs(code, file, function_failed, description)
                values ('500', 'credit_controller.py', 'get_credits', '{str(e).replace("'", "")}') returning id;
            """)
            return {"status": 500, "data": {}}

    def get_by_id(self, data:dict) -> dict:
        try:
            # Start Transaction
            conn = self.db.connect_db()
            query_credit = self.db.transaction(f"""
                select c.id as credit_id,c.state as state_credit,*, (select value from interests i where i.id = c.id_interest) as porcent
                from credits c
                inner join clients c2 on c2.id = c.id_client
                where c.id ='{data['id']}';
            """,
            conn)
            cursor = query_credit[1]
            get_credit = query_credit[0]
            self.db.transaction_close(conn, cursor)
            # Finish Transaction
            return {"status": 200, "data": get_credit}
        except Exception as e:
            self.db.execute_one(f"""
                insert into logs(code, file, function_failed, description)
                values ('500', 'credit_controller.py', 'get_by_id', '{str(e).replace("'", "")}') returning id;
            """)
            return {"status": 500, "data": {}}

    def credit_modify(self, data:dict) -> dict:
        try:
            # Start Transaction
            conn = self.db.connect_db()
            search_interest = self.db.transaction(f"""
                select *
                from interests i 
                where value ='{round(float(data['porcent']), 2)}'
                order by id desc;
            """,
            conn)
            cursor = search_interest[1]
            get_interest = search_interest[0]
            if len(get_interest)<1:
                search_interest = self.db.transaction_execute(f"""
                    insert into interests (value)
                    values('{round(float(data['porcent']), 2)}') returning *;
                """,
                cursor,
                conn)
                cursor = search_interest[1]
                get_interest = search_interest[0]
            modify_credit = self.db.transaction_execute(f"""
                update credits 
                set value = '{data['value']}',
                quota = '{data['quota']}',
                utility = '{data['utility']}',
                state = '{data['state']}',
                id_interest = '{get_interest[0]['id']}',
                id_client ='{data['id_client']}',
                comment = '{data['comment']}',
                start_credit_at = '{data['start_credit_at']}',
                updated_at = CURRENT_TIMESTAMP
                where id ='{data['id']}' returning *;
            """,
            cursor,
            conn)
            cursor = modify_credit[1]
            get_credit = modify_credit[0]
            self.db.transaction_close(conn, cursor)
            # Finish Transaction
            return {"status": 200}
        except Exception as e:
            self.db.execute_one(f"""
                insert into logs(code, file, function_failed, description)
                values ('500', 'credit_controller.py', 'credit_modify', '{str(e).replace("'", "")}') returning id;
            """)
            return {"status": 500, "data": {}}

    def find_by_name_email_identification(self, data: dict) -> dict:
        try:
            offset = 20
            calculate = int(data['page'])*offset
            calculate = calculate - offset
            state = '1'
            if data['state'] == "active":
                state = '1'
            elif data['state'] == 'inactive':
                state= '0'
            if int(data['page']) == 0 or int(data['page']) == 1:
                calculate = 0
            # Start Transaction
            conn = self.db.connect_db()
            query = f"""
                select c2.id as credit_id,c2.state as state_credit,*, count(*) over() as total, (select count(id) from payments p where c2.id=p.id_credit) as quote_paid
                ,(c2.utility::float/c2.quota) as value_quote
                from clients as c
                inner join credits c2 on c2.id_client = c.id
                where ((concat(c.first_name::text , ' ' , c.last_name::text) like '%{data['data'].replace(' ', '%')}%'))
                or ((concat(c.first_name::text , ' ' , c.last_name::text) like '%{data['data'].replace(' ', '%')}%')) 
                or (email like '%{data['data']}%')
                or (first_name like '%{data['data']}%')
                or (last_name like '%{data['data']}%')
                or (number_identification like '%{data['data']}%')
                or (c2.code2 like '%{data['data']}%')
                and c.id in (
                        select client_id from Usuarios_clients uc where uc.Usuario_id ='{data['id']}'
                    ) 
                and c.state = 1
                """
            if data['state'] != 'all' and data['state'] != 'mora':
                query += f"""
                    and c2.state = '{state}'
                """
            elif data['state'] == 'mora':
                query += f"""
                    and c2.id in (
                        select mora.id
						from (
							select *, ( 
                                case when (split_part((
                                ((c2.start_credit_at::timestamp + cast(c2.quota || ' days' as interval)) - c2.start_credit_at)-cast ((select count(p.id) from payments p where p.id_credit=c2.id and p.state='1') || ' days' as interval)
                                )::text, ' ', 1) 
                                )='00:00:00' then('0') else (
                                split_part((
                                ((c2.start_credit_at::timestamp + cast(c2.quota || ' days' as interval)) - c2.start_credit_at)-cast ((select count(p.id) from payments p where p.id_credit=c2.id and p.state='1') || ' days' as interval)
                                )::text, ' ', 1) 
                                ) end
                            ) as cuotas_mora
							from credits as c2
						) as mora
						where mora.cuotas_mora::float >0
                    )
                """
            query += f"""and c2.owner_Usuario_id ='{data['id']}'
                limit 20 offset {calculate};
            """
            print(query)
            find_client = self.db.transaction(
                query,
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
                values ('500', 'credit_controller.py', 'find_by_name_email_identification', '{str(e).replace("'", "")}') returning id;
            """)
            return {"status": 500, "data": {}}

    def new_with_payments(self, data: dict) -> dict:
        try:
            # Start Transaction
            conn = self.db.connect_db()
            search_credits = self.db.transaction(f"""
                select *
                from credits c 
                inner join clients c2 on c2.id = c.id_client 
                where c.id_client ='{data['id_client']}'
                order by c.id desc
                limit 1;
            """,
            conn)
            cursor = search_credits[1]
            get_credits = search_credits[0]
            first_name = ""
            last_name = ""
            counter = 1
            if len(get_credits) > 0:
                if get_credits[0]['first_name'][0] == " ":
                        get_credits[0]['first_name'] = get_credits[0]['first_name'][1:]
                if get_credits[0]['last_name'][0] == " ":
                    get_credits[0]['last_name'] = get_credits[0]['last_name'][1:]
                first_name = get_credits[0]['first_name'].split(' ')
                last_name = get_credits[0]['last_name'].split(' ')
                if " " in get_credits[0]['first_name']:
                    first_name = first_name[0]
                else:
                    first_name = get_credits[0]['first_name']
                if " " in get_credits[0]['last_name']:
                    last_name = last_name[0]
                else:
                    last_name = get_credits[0]['last_name']
                last_number_code= get_credits[0]['code2'].split('-')
                counter = int(last_number_code[1])+1
            else:
                query_client = self.db.transaction_execute(f"""
                    select *
                    from clients c 
                    where id ='{data['id_client']}';
                """,
                cursor,
                conn);
                cursor = query_client[1]
                get_client = query_client[0]
                if get_client[0]['first_name'][0] == " ":
                        get_client[0]['first_name'] = get_client[0]['first_name'][1:]
                if get_client[0]['last_name'][0] == " ":
                    get_client[0]['last_name'] = get_client[0]['last_name'][1:]
                first_name = get_client[0]['first_name'].split(' ')
                last_name = get_client[0]['last_name'].split(' ')
                if " " in get_client[0]['first_name']:
                    first_name = first_name[0]
                else:
                    first_name = get_client[0]['first_name']
                if " " in get_client[0]['last_name']:
                    last_name = last_name[0]
                else:
                    last_name = get_client[0]['last_name']
            search_interest = self.db.transaction_execute(f"""
                select *
                from interests i 
                where value ='{round(float(data['porcent']), 2)}'
                order by id desc;
            """,
            cursor,
            conn)
            cursor = search_interest[1]
            get_interest = search_interest[0]
            if len(get_interest)<1:
                search_interest = self.db.transaction_execute(f"""
                    insert into interests (value)
                    values('{round(float(data['porcent']), 2)}') returning *;
                """,
                cursor,
                conn)
                cursor = search_interest[1]
                get_interest = search_interest[0]
            # total_payment = int(data['total_payment'])*int(data['value_payment'])
            new_credit = self.db.transaction_execute(f"""
                insert into credits (id_client, owner_Usuario_id, value, quota, value_paid, utility, id_interest, code, comment, start_credit_at, state, code2)
                values ('{data['id_client']}', '{data['Usuario_id']}', '{data['value']}', '{data['quota']}', '{data['value_payment']}', '{data['utility']}', '{get_interest[0]['id']}', '{generate_string.generate()}', '{data['comment']}','{data['start_credit_at']}', '{data['state']}', '{first_name}{last_name}-{counter}') returning *;
            """,
            cursor,
            conn)
            cursor = new_credit[1]
            get_credit = new_credit[0]
            for index, payment in enumerate(range(int(data['total_payment']))):
                new_quota = self.db.transaction_execute(f"""
                    insert into payments (owner_Usuario_id, id_credit, way_to_pay, code_transaction, description, value, created_by, start_payment_at, updated_by)
                    values('{data['Usuario_id']}', '{get_credit[0]['id']}', '{data['way_to_pay']}', '{generate_string.generate()}', '{data['comment_payment']}', '{int(float(data['value_payment'])/int(data['total_payment']))}', '{data['Usuario_id']}', now(), '{data['Usuario_id']}') returning *;
                """,
                cursor,
                conn);
                cursor = new_quota[1]
                get_quota = new_quota[0]
            self.db.transaction_close(conn, cursor)
            # Finish Transaction
            return {"status": 200}
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.db.execute_one(f"""
                insert into logs(code, file, function_failed, description)
                values ('500', 'credit_controller.py', 'new_with_payments', '{str(e).replace("'", "")+ " " +str(fname)+" "+str(exc_tb.tb_lineno)}') returning id;
            """)
            return {"status": 500, "data": {}}

    def get_all_credit(self) -> dict:
        try:
            # Start Transaction
            conn = self.db.connect_db()
            new_credit = self.db.transaction(f"""
                select *, c.code, c.id as credit_id, c.utility, c.quota, c.value_paid as credit_paid
                from credits c
                inner join clients c2 on c2.id = c.id_client
                where c.state ='1'
                and c.value_paid::float < c.utility::float 
                order by c2.first_name asc;
            """,
            conn)
            cursor = new_credit[1]
            get_credit = new_credit[0]
            self.db.transaction_close(conn, cursor)
            # Finish Transaction
            return {"status": 200, "data": get_credit}
        except Exception as e:
            self.db.execute_one(f"""
                insert into logs(code, file, function_failed, description)
                values ('500', 'credit_controller.py', 'get_all_credit', '{str(e).replace("'", "")}') returning id;
            """)
            return {"status": 500, "data": {}}

    def get_all_credit_by_client_id(self, data:dict) -> dict:
        try:
            # Start Transaction
            conn = self.db.connect_db()
            find_credits = self.db.transaction(f"""
                select *
                from credits c 
                where id_client ='{data['client_id']}';
            """,
            conn)
            cursor = find_credits[1]
            get_credit = find_credits[0]
            self.db.transaction_close(conn, cursor)
            # Finish Transaction
            return {"status": 200, "data": get_credit}
        except Exception as e:
            self.db.execute_one(f"""
                insert into logs(code, file, function_failed, description)
                values ('500', 'credit_controller.py', 'get_all_credit_by_client_id', '{str(e).replace("'", "")}') returning id;
            """)
            return {"status": 500, "data": {}}

    def set_credit_code(self, data:dict) -> dict:
        try:
            # Start Transaction
            conn = self.db.connect_db()
            find_credits = self.db.transaction(f"""
                select *, c.id as id
                from credits c 
                inner join clients c2 on c2.id = c.id_client 
                order by c2.id asc
            """,
            conn)
            cursor = find_credits[1]
            get_credit = find_credits[0]
            counter = 1
            # Finish Transaction
            for index, data in enumerate(get_credit):
                if data['first_name'][0] == " ":
                    data['first_name'] = data['first_name'][1:]
                if data['last_name'][0] == " ":
                    data['last_name'] = data['last_name'][1:]
                first_name = data['first_name'].split(' ')
                last_name = data['last_name'].split(' ')
                if " " in data['first_name']:
                    first_name = first_name[0]
                else:
                    first_name = data['first_name']
                if " " in data['last_name']:
                    last_name = last_name[0]
                else:
                    last_name = data['last_name']
                exists_code2 = self.db.transaction_execute(f"""
                    select *
                    from credits c 
                    where code2 ='{first_name}{last_name}-{counter}';
                """,
                cursor,
                conn);
                cursor = exists_code2[1]
                get_exists_code = exists_code2[0]
                if len(get_exists_code) >0:
                    counter += 1
                else:
                    counter = 1
                update_credit = self.db.transaction_execute(f"""
                    update credits 
                    set code2 ='{first_name}{last_name}-{counter}'
                    where id = '{data['id']}'
                    returning *;
                """,
                cursor,
                conn);
                cursor = update_credit[1]
                get_quota = update_credit[0]
            self.db.transaction_close(conn, cursor)
            return {"status": 200, "data": get_credit}
        except Exception as e:
            self.db.execute_one(f"""
                insert into logs(code, file, function_failed, description)
                values ('500', 'credit_controller.py', 'set_credit_code', '{str(e).replace("'", "")}') returning id;
            """)
            return {"status": 500, "data": {}}
        
    def active_inactive_credits(self)->dict:
        try:
            # Start Transaction
            conn = self.db.connect_db()
            get_credits = self.db.transaction(f"""
                select (
                    select count(id)
                    from credits c
                ) as total_credits,
                (
                    select count(id)
                    from credits c
                    where c.state ='1'
                ) as active_credits,
                (
                    select count(id)
                    from credits c
                    where c.state ='0'
                )as disable_credits;
            """,
            conn)
            cursor = get_credits[1]
            get_credit = get_credits[0]
            self.db.transaction_close(conn, cursor)
            return{"status": 200, "data": get_credit[0]}
        except Exception as e:
            self.db.execute_one(f"""
                insert into logs(code, file, function_failed, description)
                values ('500', 'credit_controller.py', 'active_inactive_credits', '{str(e).replace("'", "")}') returning id;
            """)
            return {"status": 500, "data": {}}