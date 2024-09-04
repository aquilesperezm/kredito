from models.client_model import ClientModelNew, ClientModelModify
import sys, os

class ClientController:

    def __init__(self, db:any) -> None:
        self.db = db

    def get_by_Usuario_id(self, id, page) -> dict:
        try:
            offset = 20
            calculate = page*offset
            calculate = calculate - offset
            if page == 0 or page == 1:
                calculate = 0
            # Start Transaction
            conn = self.db.connect_db()
            get_clients = self.db.transaction(f"""
                select *, count(*) OVER() AS total
                from clients as c
                where c.id in (
                        select client_id from Usuarios_clients uc where uc.Usuario_id ='{id}'
                    ) and c.state = 1 limit 20 offset {calculate};
            """, conn)
            cursor = get_clients[1]
            clients = get_clients[0]
            if len(clients) ==0:
                total_rows = 0
            else:
                total_rows = clients[0]['total']

            self.db.transaction_close(conn, cursor)
            # Finish Transaction
            return {"status": 200, "total": total_rows, "clients": clients}
        except Exception as e:
            self.db.execute_one(f"""
                insert into logs(code, file, function_failed, description)
                values ('500', 'client_controller.py', 'get_by_Usuario_id', '{str(e)}') returning id;
            """)
            return {"status": 500, "data": {}}

    def create(self, client: ClientModelNew)-> dict:
        try:            
            # Start Transaction
            conn = self.db.connect_db()
            exists_email = self.db.transaction(f"""
                select *
                from clients c 
                where email = '{client['email']}';
            """,
            conn)
            cursor = exists_email[1]
            get_client = exists_email[0]
            if get_client:
                return {"status": 409, "data": {}}
            new_client = self.db.transaction_execute(f"""
                insert into clients(first_name, last_name, type_identification, number_identification, phone, email, address, address_two, alias)
                values('{client['first_name']}', '{client['last_name']}', '{client['type_identification']}', '{client['number_identification']}', '{client['phone']}', '{client['email']}', '{client['address']}', '{client['address_two']}', '{client['alias']}') returning *;""",
                cursor,
                conn);
            cursor = new_client[1]
            clients = new_client[0]
            insert_client_Usuario = self.db.transaction_execute(f"""
                insert into Usuarios_clients (Usuario_id, client_id)
                values('{client['created_by']}', '{clients[0]['id']}') returning *;
                """, 
                cursor,
                conn)
            cursor = insert_client_Usuario[1]
            client_Usuario = insert_client_Usuario[0]
            self.db.transaction_close(conn, cursor)
            # Finish Transaction
            return {"status": 200}
        except Exception as e:
            self.db.execute_one(f"""
                insert into logs(code, file, function_failed, description)
                values ('500', 'client_controller.py', 'create', '{str(e).replace("'", "")}') returning id;
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
                select *, count(*) over() as total
                from clients as c
                where ((concat(c.first_name::text , ' ' , c.last_name::text) like '%{data['data'].replace(' ', '%')}%'))
                or (email like '%{data['data']}%'
                or first_name like '%{data['data']}%'
                or last_name like '%{data['data']}%'
                or number_identification like '%{data['data']}%')
                and c.id in (
                        select client_id from Usuarios_clients uc where uc.Usuario_id ='{data['id']}'
                    ) and c.state = 1
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
                values ('500', 'client_controller.py', 'find_by_name_email_identification', '{str(e).replace("'", "")}') returning id;
            """)
            return {"status": 500, "data": {}}
    
    def modify(self, client: ClientModelModify)-> dict:
        try:
            # Start Transaction
            conn = self.db.connect_db()
            exists_email = self.db.transaction(f"""
                select *
                from clients c 
                where email = '{client['email']}';
            """,
            conn)
            cursor = exists_email[1]
            get_client = exists_email[0]
            if len(get_client)>0:
                if int(get_client[0]['id']) != int(client['id']) and (get_client[0]['email'] == client['email']):
                    return {"status": 409, "data": {}}
            update_client = self.db.transaction_execute(f"""
                update clients
                    set first_name='{client['first_name']}', 
                    last_name='{client['last_name']}', 
                    type_identification='{client['type_identification']}', 
                    number_identification='{client['number_identification']}', 
                    phone='{client['phone']}', 
                    email='{client['email']}', 
                    address='{client['address']}',
                    address_two='{client['address_two']}', 
                    alias='{client['alias']}',
                    state='{client['state']}',
                    updated_at=now() 
                where id ='{client['id']}'  returning *;
            """,
            cursor,
            conn)
            cursor = update_client[1]
            updated_client = update_client[0]
            self.db.transaction_close(conn, cursor)
            # Finish Transaction
            return{"status": 200}
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.db.execute_one(f"""
                insert into logs(code, file, function_failed, description)
                values ('500', 'client_controller.py', 'modify', '{str(e).replace("'", "")+ " " +str(fname)+" "+str(exc_tb.tb_lineno)}') returning id;
            """)
            return {"status": 500, "data": {}}

    def get_by_id(self, client_id:dict) ->dict:
        try:
            # Start Transaction
            conn = self.db.connect_db()
            exists_email = self.db.transaction(f"""
                select *
                from clients c 
                where id='{client_id['id']}';
            """,
            conn)
            cursor = exists_email[1]
            get_client = exists_email[0]
            self.db.transaction_close(conn, cursor)
            return{"status": 200, "data": get_client}
        except Exception as e:
            self.db.execute_one(f"""
                insert into logs(code, file, function_failed, description)
                values ('500', 'client_controller.py', 'get_by_id', '{str(e).replace("'", "")}') returning id;
            """)
            return {"status": 500, "data": {}}

    def get_all(self) -> dict:
        try:
            # Start Transaction
            conn = self.db.connect_db()
            get_clients = self.db.transaction(f"""
               select *, count(id) over() as total
               from clients c 
               order by last_name asc;
            """,
            conn)
            cursor = get_clients[1]
            get_client = get_clients[0]
            self.db.transaction_close(conn, cursor)
            return{"status": 200, "data": get_client}
        except Exception as e:
            self.db.execute_one(f"""
                insert into logs(code, file, function_failed, description)
                values ('500', 'client_controller.py', 'get_all', '{str(e).replace("'", "")}') returning id;
            """)
            return {"status": 500, "data": {}}
        
    def active_diable_clients(self) -> dict:
        try:
            # Start Transaction
            conn = self.db.connect_db()
            get_clients = self.db.transaction(f"""
                select (
                    select count(id)
                    from clients c
                ) as total_clients,
                (
                    select count(id)
                    from clients c
                    where c.state ='1'
                ) as active_clients,
                (
                    select count(id)
                    from clients c
                    where c.state ='0'
                )as disable_clients;
            """,
            conn)
            cursor = get_clients[1]
            get_client = get_clients[0]
            self.db.transaction_close(conn, cursor)
            return{"status": 200, "data": get_client[0]}
        except Exception as e:
            self.db.execute_one(f"""
                insert into logs(code, file, function_failed, description)
                values ('500', 'client_controller.py', 'active_diable_clients', '{str(e).replace("'", "")}') returning id;
            """)
            return {"status": 500, "data": {}}