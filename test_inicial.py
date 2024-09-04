from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from main import app
from classes.models import ClienteCreate, ClienteFilter, CreditoCreate, Exportacion, PagoCreate, ParamExportacion
from datetime import date

client = TestClient(app)
token = ''
r2 = None
r3 = None
r4 = None


def test_login():
    global token
    r1 = client.post(
        "/Usuarios/login", data={"Usuarioname": "admin", "password": "app2002"}
    )
    assert r1.status_code == 200
    token = r1.json()["access_token"]


def test_create_client1():
    global r2
    r2 = client.post(
        '/clientes/create',
        json=ClienteCreate(nombres='ari', apellidos='c r', celular='4545',
                           comentarios='', direccion='e2y3', email='a@cu.cu',
                           estado=9, tipo_de_identificacion_id=7,
                           numero_de_identificacion='007', telefono='55430878').dict(),
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r2.status_code == 200


def test_create_client2():
    r22 = client.post(
        '/clientes/create',
        json=ClienteCreate(nombres='pedro', apellidos='p p', celular='4546',
                           comentarios='', direccion='e2y4', email='p@cu.cu',
                           estado=9, tipo_de_identificacion_id=7,
                           numero_de_identificacion='008', telefono='55332345').dict(),
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r22.status_code == 200


def test_create_credit():
    global r3
    r3 = client.post(
        '/creditos/create',
        json=jsonable_encoder(CreditoCreate(comentario="primer credito",
                                            cobrador_id=1,
                                            fecha_de_aprobacion=date.today(),
                                            numero_de_cuotas=5,
                                            tasa_de_interes=20,
                                            monto=100,
                                            estado=9,  # activo
                                            frecuencia_del_credito_id=14,  # mensual
                                            dias_adicionales=3,
                                            tipo_de_mora_id=22,  # valor fijo
                                            valor_de_mora=50,
                                            owner_id=r2.json()['owner_id'],
                                            garante_id=None
                                            )),
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r3.status_code == 200


def test_create_pago():
    r4 = client.post(
        '/pagos/create',
        json=jsonable_encoder(PagoCreate(comentario='primer pago',
                                         credito_id=r3.json()['id'],
                                         fecha_de_pago=date.today(), valor_del_pago=60)),
        headers={"Authorization": f"Bearer {token}"}
    )
    print('pago:', r4.json(), '\n\n')
    assert r4.status_code == 200


def test_comprobante_de_pago():
    r5 = client.get(
        '/pagos/comprobante_de_pago_by_id_pago/1',
        headers={"Authorization": f"Bearer {token}"}
    )
    print('comprobante de pago', r5.json(), '\n\n')
    assert r5.status_code == 200


def test_cliente_filter():
    r6 = client.post(
        '/clientes/filtrar',
        json=jsonable_encoder(
            ClienteFilter(
                texto='ari',
                fecha_inicial=date(2020, 1, 1),
                fecha_final=date(2024, 3, 8),
            )),
        headers={"Authorization": f"Bearer {token}"}
    )
    print('filtrar cliente', r6.json(), '\n\n')

    assert r6.status_code == 200


def test_obtener_credito():
    r7 = client.get(
        '/creditos/by_id/1',
        headers={"Authorization": f"Bearer {token}"}
    )
    print('get credito', r7.json(), '\n\n')
    assert r7.status_code == 200


test_login()
test_create_client1()
test_create_client2()
test_create_credit()
test_create_pago()
test_comprobante_de_pago()
test_cliente_filter()
test_obtener_credito()
