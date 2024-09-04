from classes.models import Configuracion


def get_config_value(session, key):
    conf = session.query(Configuracion).where(
        Configuracion.key == key).first()
    return conf.value
