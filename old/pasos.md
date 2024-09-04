## Pasos para poner a funcionar el backend

### Instalar python
- Descargar desde
[sitio oficial de python](https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe)
- instalar.

### Crear entorno virtual y activarlo:
- comando: `python -m venv env`
- comando: `.\env\Scripts\activate`

### Instalar las dependencias:
- comando `python -m pip install -r requirements.txt`

### Ejecutar
- comando `python main.py`
- o desde el vscode: `Run/Run without debugging`

---

Cada vez que quuieras comenzar de 0, borra el archivo `database/deudas.sqlite`

Para los tests puedes ejecutar el archivo *test_inicial.py* con el comando `python test_inicial.py`