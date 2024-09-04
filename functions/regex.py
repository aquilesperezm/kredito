import re

class RegexValidate():

    def __init__(self) -> None:
        self.valid_email = "^([A-Za-z]|[0-9])+@([A-Za-z]|[0-9])+.([A-Za-z]|[0-9])+$"
        self.valid_password = "^([A-Za-z]|[0-9])+$"

    def validate_email(self, data:str)->bool:
        return re.match(self.valid_email, data)

    def validate_password(self, data:str)->bool:
        return re.match(self.valid_password, data)