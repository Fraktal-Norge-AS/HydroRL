from server.appsettings import appSettings
import sqlalchemy


def create_engine():
    engine = sqlalchemy.create_engine(appSettings.get_connection_string(), connect_args={"timeout": 60})
    return engine
