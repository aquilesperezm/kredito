from typing import TypedDict

class ClientModelNew(TypedDict):
    first_name: str
    last_name: str
    type_identification: str
    number_identification: str
    phone: str
    email: str
    address: str
    address_two: str
    alias: str
    created_by: str

class ClientModelModify(TypedDict):
    id: str
    first_name: str
    last_name: str
    type_identification: str
    number_identification: str
    phone: str
    email: str
    address: str
    address_two: str
    alias: str
    state: str