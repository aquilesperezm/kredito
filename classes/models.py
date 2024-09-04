# from __future__ import annotations
from datetime import date
from typing import Dict, List, Optional
from sqlmodel import Relationship, SQLModel, Field, Column
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
#from sqlalchemy.ext.declarative import declarative_base
#from sqlalchemy import Column, Integer, String, Float
#from datetime import datetime
import pydantic
from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy.orm import relationship
from database.database import get_session



def getListRelationchip(model_here: str, foreign_model, back_populates: str) -> Relationship:
    """Ayuda a crear la relacion cuando hay mas de una propiedad que es el mismo modelo (cuando es lista)

    asumo que si backpopulate es 'hola' entonces fk es 'hola_id'
    """
    return Relationship(
        back_populates=f"{back_populates}",
        sa_relationship_kwargs={
            "primaryjoin": f"foreign({foreign_model}.{back_populates}_id)=={model_here}.id",
            # "lazy": "joined",
        },
    )


def getRelationchip(model_here: str, foreign_key_here: str, back_populates: str) -> Relationship:
    """Ayuda a crear la relacion cuando hay mas de una propiedad que es el mismo modelo (cuando es uno solo)'
    """
    return Relationship(
        back_populates=f"{back_populates}",
        sa_relationship_kwargs=dict(
            foreign_keys=f"[{model_here}.{foreign_key_here}]"),
    )

class Config:
    arbitrary_types_allowed = True

class TipoEnumeradorCreate(SQLModel):
    nombre: str


class TipoEnumeradorUpdate(TipoEnumeradorCreate):
    ...


class TipoEnumerador(SQLModel, table=True):
    
    id: Optional[int] = Field(default=None, primary_key=True)
   
    nombre: str
    enumeradores: List['Enumerador'] = Relationship(
        back_populates='tipo_enumerador')
    created_at: date = Field(default=date.today(), nullable=False)
    last_edited: date = Field(
        default_factory=date.today, nullable=False)


class EnumeradorCreate(SQLModel):
    tipo_enumerador_id: int
    nombre: str


class EnumeradorUpdate(SQLModel):
    nombre: str


class Enumerador(SQLModel, table=True):
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    tipo_enumerador_id: int = Field(foreign_key='tipoenumerador.id')
    tipo_enumerador: TipoEnumerador = Relationship(
        back_populates='enumeradores')
    nombre: str
   
    usuarios: List['Usuario'] = Relationship(back_populates='rol',sa_relationship_kwargs=
        {'primaryjoin': "foreign(Usuario.rol_id) == Enumerador.id", "uselist": True})
    
    sucursales_usuarios: List['Usuario'] =Relationship(back_populates='sucursal',sa_relationship_kwargs=
        {'primaryjoin': "foreign(Usuario.sucursal_id) == Enumerador.id", "uselist": True})
    
    clientes: List['Cliente'] = Relationship(back_populates='tipo_de_identificacion',sa_relationship_kwargs=
        {'primaryjoin': "foreign(Cliente.tipo_de_identificacion_id) == Enumerador.id", "uselist": True})
    
    zonas: List['Cliente'] = Relationship(back_populates='zona',sa_relationship_kwargs=
        {'primaryjoin': "foreign(Cliente.zona_id) == Enumerador.id", "uselist": True})

    sucursales_clientes: List['Cliente'] = Relationship(back_populates='sucursal',sa_relationship_kwargs=
        {'primaryjoin': "foreign(Cliente.sucursal_id) == Enumerador.id", "uselist": True})
    
    creditosfr: List['Credito'] = Relationship(
        back_populates='frecuencia_del_credito', sa_relationship_kwargs=
        {'primaryjoin': "foreign(Credito.frecuencia_del_credito_id) == Enumerador.id", "uselist": True})
    
    creditostm: List['Credito'] = Relationship(
        back_populates='tipo_de_mora', sa_relationship_kwargs=
        {'primaryjoin': "foreign(Credito.tipo_de_mora_id) == Enumerador.id", "uselist": True})
    
    roles_by_reportes: List['ExportacionByUser'] = Relationship(back_populates='rol_config',sa_relationship_kwargs=
        {'primaryjoin': "foreign(ExportacionByUser.rol_id) == Enumerador.id", "uselist": True})
    
    
    
    created_at: date = Field(default=date.today(), nullable=False)
    last_edited: date = Field(
        default_factory=date.today, nullable=False)


class TipoEnumeradorRead(SQLModel):
    id: int
    # tipo_enumerador_id: int
    nombre: str
    enumeradores: List[Enumerador]


class ClienteBase(SQLModel):
    nombres: str
    apellidos: str
    tipo_de_identificacion_id: int
    numero_de_identificacion: str
    celular: str
    telefono: str
    email: str
    direccion: str
    comentarios: str
    estado: int
    sucursal_id: int
    zona_id: int
    referencia_id: int = Field(
        foreign_key='cliente.id', default=None)


class ClienteFilter(SQLModel):
    consulta: Optional[str] = None
    fecha_inicial: Optional[date] = None
    fecha_final: Optional[date] = None
    saldo_por_pagar: Optional[bool] = None
    en_mora: Optional[bool] = None


class ClienteCreate(ClienteBase):
    ...
    

class ClienteUpdate(SQLModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    tipo_de_identificacion_id: Optional[int] = None
    numero_de_identificacion: Optional[str] = None
    celular: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    comentarios: Optional[str] = None
    estado: Optional[int] = None
    zona_id: int
    sucursal_id: int
    referencia_id: Optional[int] = None


class Cliente(ClienteBase, table=True):
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    owner_id: int = Field(foreign_key='usuario.id')
    owner: 'Usuario' = Relationship(back_populates='clientes')
    
    referencia_id: int = Field(foreign_key='cliente.id', default=None)
    referencia: 'Cliente' = Relationship(
        back_populates='referencias',
        sa_relationship_kwargs=dict(remote_side='Cliente.id')
    )
   
    """
    Observacion: Cuando existe una tabla con varias relaciones a una misma tabla, existe ambiguedad en la llave
    foranea, por tanto se debe especificar la llave foranea
      Ejemplo:
          Cliente (tipo_de_identificador_id) -> Enumerador.id
          Cliente (zona_id)                  -> Enumerador.id
          Clinete (sucursal_id)              -> Enumerador.id
         
    
    """
    tipo_de_identificacion_id: int = Field(foreign_key='enumerador.id')
    tipo_de_identificacion: Enumerador = Relationship(back_populates='clientes', sa_relationship_kwargs=
                    {'primaryjoin': "foreign(Cliente.tipo_de_identificacion_id) == Enumerador.id", "uselist": False})
    
    zona_id: int = Field(foreign_key='enumerador.id')
    zona: Enumerador = Relationship(back_populates='zonas', sa_relationship_kwargs=
                    {'primaryjoin': "foreign(Cliente.zona_id) == Enumerador.id", "uselist": False})
                
   
    sucursal_id: int = Field(foreign_key='enumerador.id')
    sucursal: Enumerador = Relationship(back_populates='sucursales_clientes', sa_relationship_kwargs=
                    {'primaryjoin': "foreign(Cliente.sucursal_id) == Enumerador.id", "uselist": False})
    
    
    # relacion recursiva
    referencias: List['Cliente'] = Relationship(back_populates='referencia')

    creditos: List['Credito'] = getListRelationchip(
        'Cliente', 'Credito', 'owner')
    
    creditos_en_garante: List['Credito'] = getListRelationchip(
        'Cliente', 'Credito', 'garante')
    
    created_at: date = Field(default=date.today(), nullable=False)
    last_edited: date = Field(
        default_factory=date.today, nullable=False)


# -------------- User -------------- #
class UserBase(SQLModel):
    nombres: str = Field(min_length=5)
    apellidos: str = Field(min_length=5)
    login_name: str = Field(min_length=2)
    password: str = Field(min_length=5)
    rol_id: int
    sucursal_id:int
    
    

class UserCreate(UserBase):
    ...


class Usuario(UserBase, table=True):
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    nombres: str = None
    apellidos: str = None 
    clientes: List[Cliente] = Relationship(back_populates='owner')
    
    rol_id: int = Field(foreign_key='enumerador.id')
    rol: Enumerador = Relationship(back_populates='usuarios', sa_relationship_kwargs=
                    {'primaryjoin': "foreign(Usuario.rol_id) == Enumerador.id", "uselist": False})
    
    sucursal_id: int = Field(foreign_key='enumerador.id')
    sucursal: Enumerador = Relationship(back_populates='sucursales_usuarios', sa_relationship_kwargs=
                    {'primaryjoin': "foreign(Usuario.sucursal_id) == Enumerador.id", "uselist": False})
     
    creditoscobrados: List['Credito'] = Relationship(back_populates='cobrador',sa_relationship_kwargs=
        {'primaryjoin': "foreign(Credito.cobrador_id) == Usuario.id", "uselist": True}) 
    
    creadores: List['Credito'] = Relationship(back_populates='creador',sa_relationship_kwargs=
        {'primaryjoin': "foreign(Credito.creador_id) == Usuario.id", "uselist": True}) 
          
    created_at: date = Field(default=date.today(), nullable=False)
    last_edited: date = Field(
        default_factory=date.today, nullable=False)
    

class UserUpdate(SQLModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    login_name: str # required
    apellidos: Optional[str] = None
    password: Optional[str] = None
    rol_id: Optional[int] = None
    sucursal_id: Optional[int] = None


class UserRead(UserBase):
    id: int
    #clientes: List[Cliente] = []


class UserReadWithRol(SQLModel):
    id: int
    nombres:str
    apellidos:str
    sucursal_id: int | None
    login_name: str
    # clientes: List[Cliente] = []
    # rol: Enumerador
    rol: str


class ClienteRead(ClienteBase):
    id: int
    owner: Optional[Usuario]


# --------------------- credito --------------------- #

class CreditoBase(SQLModel):
    comentario: str
    cobrador_id: int
    fecha_de_aprobacion: date
    numero_de_cuotas: int
    # la tasa de interes siempre se estima en porciento
    tasa_de_interes: int
    # cantidad solicitada a prestar
    monto: int
    estado: int
    frecuencia_del_credito_id: int
    dias_adicionales: int
    tipo_de_mora_id: int
    valor_de_mora: int
    creador_id: int = Field(foreign_key='usuario.id')

class CreditoUpdate(SQLModel):
    comentario: Optional[str] = None
    cobrador_id: Optional[int] = None
    fecha_de_aprobacion: Optional[date] = None
    numero_de_cuotas: Optional[int] = None
    tasa_de_interes: Optional[int] = None
    monto: Optional[int] = None
    estado: Optional[int] = None
    dias_adicionales: Optional[int] = None
    tipo_de_mora_id: Optional[int] = None
    valor_de_mora: Optional[int] = None
    frecuencia_del_credito_id: Optional[int] = None
    garante_id: Optional[int] = None

    

# --------------------- pagos --------------------- #

# TODO poner en enumeradores


class PagoBase(SQLModel):
    comentario: str
    fecha_de_pago: date
    valor_del_pago: int
    # metodo_de_pago_id: int


class PagoCreate(PagoBase):
    credito_id: int = Field(foreign_key='credito.id')


class PagoUpdate(SQLModel):
    comentario: Optional[str] = None
    fecha_de_pago: Optional[date] = None
    valor_del_pago: Optional[int] = None
    # metodo_de_pago_id: Optional[int] = None


class Cuota(SQLModel, table=True):
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    numero_de_cuota: int
    fecha_de_pago: date
    fecha_de_aplicacion_de_mora: date
    valor_pagado: int
    valor_de_cuota: int
    valor_de_mora: int
    pagada: bool
    
    credito_id: int = Field(foreign_key='credito.id')
    credito: 'Credito' = Relationship(back_populates='cuotas')
    
    created_at: date = Field(default=date.today(), nullable=False)
    last_edited: date = Field(
        default_factory=date.today, nullable=False)

    # cuota está vencida si la fecha actual es mayor a la fecha de pago de la cuota 
    # y si el valor pagado es inferior al valor de la cuota más el valor de la mora
    def es_vencida(self):
         return (date.today() > self.fecha_de_pago) and (self.valor_pagado < self.valor_de_cuota + self.valor_de_mora)
    
    def total_a_pagar(self):
        return self.valor_de_cuota+self.valor_de_mora


class Pago(PagoBase, table=True):
    
    id: Optional[int] = Field(default=None, primary_key=True)
   
    credito_id: int = Field(foreign_key='credito.id')
    credito: 'Credito' = Relationship(back_populates='pagos')
    
    registrado_por_usuario_id: int
    # metodo_de_pago_id: Optional[int] = Field(foreign_key='enumerador.id')
    # metodo_de_pago: Enumerador = Relationship(back_populates='pagos')
    comprobantes_de_pago: List['ComprobanteDePago'] = Relationship(
        back_populates='pago')
    created_at: date = Field(default=date.today(), nullable=False)
    last_edited: date = Field(
        default_factory=date.today, nullable=False)


class PagoDeCuota(SQLModel, table=True):
   
    id: Optional[int] = Field(default=None, primary_key=True)
    
    numero_de_cuota: int
    abonado: int
    tiene_mora: bool
    comprobante_id: int = Field(foreign_key='comprobantedepago.id')
    comprobante: 'ComprobanteDePago' = Relationship(
        back_populates='pagos_de_cuotas')


class PagoDeCuotaSimple(SQLModel):
    numero_de_cuota: int
    abonado: int
    tiene_mora: bool


class ComprobanteDePago(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    pago_id: int = Field(foreign_key='pago.id')
    pago: 'Pago' = Relationship(back_populates='comprobantes_de_pago')
    nombre_del_cliente: str
    cedula: str
    telefono: str
    fecha: date = Field(default=date.today(), nullable=False)
    pendiente: float
    cambio: float
    comentario: str
    pagos_de_cuotas: List[PagoDeCuota] = Relationship(
        back_populates='comprobante')


class ComprobanteDePagoRead(SQLModel):
    id: int
    pago_id: int
    nombre_del_cliente: str
    cedula: str
    telefono: str
    fecha: date
    pendiente: float
    comentario: str
    pagos_de_cuotas: List[PagoDeCuotaSimple]


class CreditoCreate(CreditoBase):
    owner_id: int
    garante_id: int | None


class CreditoRead(CreditoBase):
    id: int
    owner_id: int
    created_at: date
    last_edited: date
    frecuencia_del_credito: Enumerador
    tipo_de_mora: Enumerador
    pagos: List[Pago]
    cuotas: List[Cuota]
    garante_id: int | None
    
    


class Credito(CreditoBase, table=True):
    
    id: Optional[int] = Field(default=None, primary_key=True)
   
    owner_id: int = Field(foreign_key='cliente.id')
    owner: Cliente = getRelationchip('Credito', 'owner_id', 'creditos')
    
    frecuencia_del_credito_id: int = Field(foreign_key="enumerador.id")
    frecuencia_del_credito: Enumerador = Relationship(back_populates='creditosfr', sa_relationship_kwargs=
        {'primaryjoin': "foreign(Credito.frecuencia_del_credito_id) == Enumerador.id", "uselist": False})
   
    tipo_de_mora_id: int = Field(foreign_key="enumerador.id")
    tipo_de_mora: Enumerador = Relationship(back_populates='creditostm', sa_relationship_kwargs=
        {'primaryjoin': "foreign(Credito.tipo_de_mora_id) == Enumerador.id", "uselist": False})
    
    cobrador_id: int = Field(foreign_key="usuario.id")
    cobrador: Usuario = Relationship(back_populates='creditoscobrados', sa_relationship_kwargs=
        {'primaryjoin': "foreign(Credito.cobrador_id) == Usuario.id", "uselist": False})
    
    creador_id: int = Field(foreign_key="usuario.id")
    creador: Usuario = Relationship(back_populates='creadores', sa_relationship_kwargs=
        {'primaryjoin': "foreign(Credito.creador_id) == Usuario.id", "uselist": False})
    
    #valor_deuda: float = Field(default=None,nullable=True)
    
    pagos: List[Pago] = Relationship(back_populates='credito')
    cuotas: List[Cuota] = Relationship(back_populates='credito')
    garante_id: int = Field(foreign_key="cliente.id")
    garante: Cliente = getRelationchip(
        'Credito', 'garante_id', 'creditos_en_garante')
    created_at: date = Field(default=date.today(), nullable=False)
    last_edited: date = Field(
        default_factory=date.today, nullable=False)
   
    # by kelex01: autogenerated this property
    
    def total_pagado(self)->float:
        """_summary_
            Devuelve el total de todos las cuotas que ya estan pagadas hasta la fecha de hoy
        Returns:
            float: _description_
        """
        hoy = date.today()
        total:float = 0
        for cuota in self.cuotas:
            if cuota.pagada and cuota.fecha_de_pago < hoy:
                total += cuota.valor_pagado
        return total

    def total_de_deuda_actual(self):
        total = 0
        for cuota in self.cuotas:
            total += cuota.total_a_pagar() - cuota.valor_pagado
        return total
    
    # --------------------- Nuevos metodos para el model Credito ----------------------------------
    def get_total_cuotas_no_pagadas(self) -> float:
        """_summary_
            Devuelve la sumatoria de las cuotas que no estan pagadas, el parametro valor de cuota 
            es el valor con que se creo la cuota 
        Returns:
            float
        """
        total:float = 0.00
        c:Cuota
        for c in self.cuotas:
            if not c.pagada:
                total += float(c.valor_de_cuota)
        return total 

    def get_monto_plus_interes(self) -> float:
        """_summary_
          Devuelve el valor del monto mas el porciento del monto que representa el interes  
          
        Returns:
            float
        """
        
        return float(self.monto + ((self.monto * self.tasa_de_interes) / 100))
    
    def get_tiene_deudas(self) -> bool:
        """_summary_
            Devuelve True si el credito tiene Cuotas por pagar
        Returns:
            bool
        """
        return self.get_total_cuotas_no_pagadas() == 0    

    def get_total_cuotas_pagadas(self) -> float:
        """_summary_
            Devuelve la suma de los valores de las deudas que no estan pagadas para este credito
        Returns:
            float
        """
        total:float = 0.00
        c:Cuota
        for c in self.cuotas:
            if c.pagada:
               total += c.valor_pagado
        return total


class PagoRead(PagoBase):
    id: Optional[int]
    created_at: date
    registrado_por_usuario_id: int
    credito: Credito


class ResumenDelCredito(SQLModel):
    credito_id: Optional[int]
    hay_morosidad: bool
    valor_mora: int
    total_debe_pagar: int
    cant_cuota_mora: int
    cuotas_por_pagar: List[Cuota]


class ResumenDelCliente(SQLModel):
    cliente_id: Optional[int]
    nombres: str
    apellidos: str
    celular: str
    telefono: str
    documento: str
    resumen_de_creditos: List[ResumenDelCredito]


class Configuracion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    key: str
    value: str


class ConfiguracionUpdate(SQLModel):
    key: str
    value: str



class Exportacion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sql_reporte: str
    codigo: str
    nombre: str
    activo: bool
    nombre_archivo: str
    comentario: str
    parametros: List['ParamExportacion'] = Relationship(
        back_populates='exportacion')
    reportes_by_usuarios: List['ExportacionByUser'] = Relationship(
        back_populates='reporte_config')

class ExportacionByUser(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    
    rol_id: int = Field(foreign_key=Enumerador.id)
    rol_config : Enumerador = Relationship(back_populates='roles_by_reportes')
    
    report_id: int = Field(foreign_key=Exportacion.id)
    reporte_config: Exportacion = Relationship(back_populates='reportes_by_usuarios')
    
    descripcion: str = None


class ParamExportacion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    exportacion_id: Optional[int] = Field(foreign_key='exportacion.id')
    exportacion: Exportacion = Relationship(back_populates='parametros')
    nombre: str
    codigo: str
    tipo_dato: str  # texto, entero, fecha, like, por defecto texto
    comentario: str
    obligatorio: bool


class ExportacionRead(SQLModel):
    id: Optional[int]
    sql_reporte: str
    codigo: str
    nombre: str
    activo: bool
    nombre_archivo: str
    comentario: str
    parametros: List['ParamExportacion']


class ExportacionResult(SQLModel):
    error: str
    resultados: List


class PrestamoFiltro(SQLModel):
    fecha_de_pago: Optional[date] = None
    saldo_por_pagar: Optional[bool] = None
    saldo_en_mora: Optional[bool] = None
    cliente: Optional[str] = None
    cliente_zona_id: Optional[int] = None
    usuario_sucursal_id: Optional[int] = None
    usuario_cobrador_id: Optional[int] = None


class Prestamo(SQLModel):
    nombre_del_cliente: str
    id_del_cliente: int
    id_del_credito: int
    fecha_de_cuota: date
    valor_de_cuota: int
    numero_de_cuota: int
    valor_de_la_mora: int
    frecuencia: Enumerador


class CK:
    cantidad_maxima_de_creditos_por_cliente = 'cantidad_maxima_de_creditos_por_cliente'
