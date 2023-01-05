import pytz
import logging

import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from log_model import LogEntry, metadata

logging.addLevelName(logging.INFO, "Information")
logging.addLevelName(logging.WARNING, "Warning")
logging.addLevelName(logging.DEBUG, "Debug")
logging.addLevelName(logging.ERROR, "Error")


class SQLiteHandler(logging.Handler):
    def __init__(self, connectionString: str):
        super(SQLiteHandler, self).__init__()

        self.engine = db.create_engine(connectionString)
        metadata.create_all(self.engine)

        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def emit(self, record: logging.LogRecord) -> None:
        entry = LogEntry(
            Timestamp=datetime.now(tz=pytz.UTC).strftime("%Y-%m-%dT%H:%M:%S"),
            Level=record.levelname,
            RenderedMessage=record.getMessage(),
            Properties="Python",
        )
        self.session.add(entry)
        self.session.commit()


class StreamToLogger:
    def __init__(self, logger, level) -> None:
        self.logger = logger
        self.level = level
        self.linebuf = ""

    def write(self, buf):
        # for line in buf.rstrip().splitlines():
        #     self.logger.log(self.level, line.rstrip())
        if buf and not buf.isspace():
            self.logger.log(self.level, buf)

    def flush(self):
        pass
