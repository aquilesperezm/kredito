from functions.encrypt_decrypt import EncryptDecrypt
from models.Usuario_model import UsuarioModelLogin
from functions.regex import RegexValidate

encrypt_decrypt = EncryptDecrypt()
regex_validate = RegexValidate()

class UsuarioController:

    def __init__(self, db:any) -> None:
        self.db = db

    def create_Usuario(self, Usuario:UsuarioModelLogin):
        try:

            valid_email = regex_validate.validate_email(Usuario['email'])
            valid_password = regex_validate.validate_password(Usuario['password'])
            if not valid_email or not valid_password:
                return {"status": 400, "data": {}}

            password_encrypt = encrypt_decrypt.encrypt(Usuario['password'])

            # Start Transaction
            conn = self.db.connect_db()
            insert_Usuario = self.db.transaction(f"""
                insert into Usuarios(email, password)
                values('{Usuario['email']}', '{password_encrypt.decode('ascii')}') returning *;
            """, conn);
            cursor = insert_Usuario[1]

            assign_role = self.db.transaction_execute(f"""
                insert into Usuarios_rolls (Usuario_id, roll_id)
                values ('{insert_Usuario[0][0]['id']}', (select id from rolls r where code ='JJ0002')) returning *;
            """, cursor, conn)
            cursor = assign_role[1]

            self.db.transaction_close(conn, cursor)
            # Finish Transaction


            return {"status": 200, "id": insert_Usuario[0][0]['id']}
        except Exception as e:
            self.db.execute_one(f"""
                insert into logs(code, file, function_failed, description)
                values ('500', 'Usuario_controller.py', 'create_Usuario', '{str(e).replace("'", "")}') returning id;
            """)
            return {"status": 500, "data": {}}

    def login_Usuario(self, Usuario:UsuarioModelLogin):
        try:
            valid_email = regex_validate.validate_email(Usuario['email'])
            valid_password = regex_validate.validate_password(Usuario['password'])
            if not valid_email or not valid_password:
                return {"status": 400, "data": {}}

            conn = self.db.connect_db()
            get_Usuario = self.db.transaction(f"""
                select *
                from Usuarios u
                where email = '{Usuario['email']}'
                and u.state = '1';
            """, conn)
            cursor = get_Usuario[1]

            if not get_Usuario[0]:
                return {"status": 404, "data": {}}

            get_roll = self.db.transaction_execute(f"""
                select r.name, r.code, r.description
                from Usuarios_rolls ur
                inner join rolls r on r.id = ur.roll_id
                where Usuario_id ='{get_Usuario[0][0]['id']}';
            """, cursor, conn)
            cursor = get_roll[1]
            get_Usuario[0][0]['rolls'] = get_roll[0]

            if get_Usuario[0][0]['id_owner'] != "" and get_Usuario[0][0]['id_owner']:
                get_Usuario[0][0]['id_Usuario'] = get_Usuario[0][0]['id']
                get_Usuario[0][0]['id'] = get_Usuario[0][0]['id_owner']

            self.db.transaction_close(conn, cursor)

            password_decrypt = encrypt_decrypt.decrypt(get_Usuario[0][0]['password'].encode('ascii'))
            if password_decrypt != Usuario['password']:
                return {"status": 201, "data": {}}

            return {"status": 200, "data": get_Usuario[0][0]}

        except Exception as e:
            self.db.execute_one(f"""
                insert into logs(code, file, function_failed, description)
                values ('500', 'Usuario_controller.py', 'login_Usuario', '{str(e).replace("'", "")}') returning id;
            """)
            return {"status": 500, "data": {}}

    def create_collector(self, data:dict) -> dict:
        try:
            valid_email = regex_validate.validate_email(data['email'])
            valid_password = regex_validate.validate_password(data['password'])
            if not valid_email or not valid_password:
                return {"status": 400, "data": {}}

            password_encrypt = encrypt_decrypt.encrypt(data['password'])

            # Start Transaction
            conn = self.db.connect_db()
            exists_Usuario = self.db.transaction(f"""
                select *
                from Usuarios u
                where (u.email ='{data['email']}') or (number_identification='{data['number_identification']}');
            """, conn);
            cursor = exists_Usuario[1]
            get_Usuarios = exists_Usuario[0]
            if len(get_Usuarios) > 0:
                return {"status": 204, "data": "Ya existe un usuario cone sa cedula o correo"}
            insert_Usuario = self.db.transaction(f"""
                insert into Usuarios(email, password, id_owner, first_name, last_name, alias, type_identification, number_identification, phone, address, description)
                values('{data['email']}', '{password_encrypt.decode('ascii')}','{data['owner_id']}', '{data['first_name']}', '{data['last_name']}', '{data['alias']}', '{data['type_identification']}', '{data['number_identification']}', '{data['phone']}', '{data['address']}', '{data['description']}') returning *;
            """, conn);
            cursor = insert_Usuario[1]

            assign_role = self.db.transaction_execute(f"""
                insert into Usuarios_rolls (Usuario_id, roll_id)
                values ('{insert_Usuario[0][0]['id']}', (select id from rolls r where code ='JJ0003')) returning *;
            """, cursor, conn)
            cursor = assign_role[1]

            self.db.transaction_close(conn, cursor)
            # Finish Transaction

            return {"status": 200, "id": insert_Usuario[0]}
        except Exception as e:
            self.db.execute_one(f"""
                insert into logs(code, file, function_failed, description)
                values ('500', 'Usuario_controller.py', 'create_collector', '{str(e).replace("'", "")}') returning id;
            """)
            return {"status": 500, "data": {}}

    def get_collector(self, data:dict) -> dict:
        try:
            offset = 7
            calculate = int(data['page'])*offset
            calculate = calculate - offset
            if int(data['page']) == 0 or int(data['page']) == 1:
                calculate = 0
            # Start Transaction
            conn = self.db.connect_db()
            query_Usuarios = self.db.transaction(f"""
                select *, count(id) over() as total
                from Usuarios
                where id_owner = '{data['Usuario_id']}'
                order by id desc
                limit 7 offset {calculate};
            """,
            conn)
            cursor = query_Usuarios[1]
            get_Usuarios = query_Usuarios[0]
            if len(get_Usuarios) ==0:
                total_rows = 0
            else:
                total_rows = get_Usuarios[0]['total']
            self.db.transaction_close(conn, cursor)
            # Finish Transaction
            return {"status": 200, "total": total_rows, "collectors": get_Usuarios}
        except Exception as e:
            self.db.execute_one(f"""
                insert into logs(code, file, function_failed, description)
                values ('500', 'Usuario_controller.py', 'get_collector', '{str(e).replace("'", "")}') returning id;
            """)
            return {"status": 500, "data": {}}

    def get_collector_by_id(self, data:dict) -> dict:
        try:
            # Start Transaction
            conn = self.db.connect_db()
            query_Usuarios = self.db.transaction(f"""
                select *
                from Usuarios u
                where id ='{data['id']}';
            """,
            conn)
            cursor = query_Usuarios[1]
            get_Usuarios = query_Usuarios[0]
            self.db.transaction_close(conn, cursor)
            # Finish Transaction
            return {"status": 200, "data": get_Usuarios}
        except Exception as e:
            self.db.execute_one(f"""
                insert into logs(code, file, function_failed, description)
                values ('500', 'Usuario_controller.py', 'get_collector_by_id', '{str(e).replace("'", "")}') returning id;
            """)
            return {"status": 500, "data": {}}

    def update_collector(self, data:dict) -> dict:
        try:
            valid_email = regex_validate.validate_email(data['email'])
            valid_password = regex_validate.validate_password(data['password'])
            if not valid_email or not valid_password:
                return {"status": 400, "data": {}}

            password_encrypt = encrypt_decrypt.encrypt(data['password'])
            # Start Transaction
            conn = self.db.connect_db()
            query_Usuarios = self.db.transaction(f"""
                update Usuarios
                set first_name = '{data['first_name']}',
                last_name = '{data['last_name']}',
                type_identification = '{data['type_identification']}',
                number_identification = '{data['number_identification']}',
                phone = '{data['phone']}',
                email = '{data['email']}',
                state = '{data['state']}',
                password = '{password_encrypt.decode('ascii')}',
                address = '{data['address']}',
                alias = '{data['alias']}',
                description = '{data['comment']}'
                where id = '{data['id']}' returning *;
            """,
            conn)
            cursor = query_Usuarios[1]
            get_Usuarios = query_Usuarios[0]
            self.db.transaction_close(conn, cursor)
            # Finish Transaction
            return {"status" : 200}
        except Exception as e:
            self.db.execute_one(f"""
                insert into logs(code, file, function_failed, description)
                values ('500', 'Usuario_controller.py', 'update_collector', '{str(e).replace("'", "")}') returning id;
            """)
            return {"status": 500, "data": {}}