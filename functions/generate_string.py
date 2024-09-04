import random
import string

class GenerateString:

    def __init__(self) -> None:
        pass

    def generate(self):
        # get random password pf length 8 with letters, digits, and symbols
        characters = string.ascii_letters + string.digits
        password = ''.join(random.choice(characters) for i in range(25))
        return password