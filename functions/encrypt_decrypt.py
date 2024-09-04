from typing import Literal
from cryptography.fernet import Fernet

class EncryptDecrypt:

    def __init__(self) -> None:
        self.key =  b'tjfzn2VzQnIBqEfoZAL6vTe16RuMlrYNaY6AhGSiUiw='
        self.fernet = Fernet(self.key)

    def encrypt(self, data:str) -> Literal:
        encMessage = self.fernet.encrypt(data.encode('ascii'))
        return encMessage


    def decrypt(self, data:str) -> str:
        decMessage = self.fernet.decrypt(data).decode('ascii')
        return decMessage