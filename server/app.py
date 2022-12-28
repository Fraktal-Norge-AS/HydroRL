import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / Path("gitsource/HydroScheduling")))

import multiprocessing

multiprocessing.set_start_method("spawn", True)
import logging
from logging.config import dictConfig
from format_exception import format_exception
import sqlite3
import numpy as np
from flask import Flask, Response, request

from requestHandler import RequestHandler

# dictConfig(appSettings.get_logging_config()) # Run once at startup
logger = logging.getLogger("dcdb_python")
logger_console = logging.getLogger("console_logger")

sqlite3.register_adapter(np.int64, lambda val: int(val))
sqlite3.register_adapter(np.int32, lambda val: int(val))

logger.info("Starting service")
try:
    reqHandler = RequestHandler()
    app = Flask(__name__)
except Exception as e:
    logger.exception("failed to start service: \n" + format_exception(e))
    raise e

logger.info("Service started")


@app.route("/create_run_settings/<path:project_uid>/<path:agent_id>")
@app.route("/create_run_settings/<path:project_uid>")
def create_run_settings(project_uid, agent_id=None):
    try:
        logger.info("call /create_run_settings/{0}/{1}".format(project_uid, agent_id if agent_id is not None else ""))
        logger_console.info("create_run_settings", project_uid, agent_id)
        return reqHandler.create_run_settings(project_uid, agent_id)
    except Exception as e:
        if agent_id is not None:
            e_str = "Exception encountered in /create_run_settings/<path:project_uid>/<path:agent_id> :\n"
        else:
            e_str = "Exception encountered in /create_run_settings/<path:project_uid>:\n"
        logger.exception(e_str + format_exception(e))
        raise e


@app.route("/start/<path:project_uid>/<path:run_id>")
def start_agents(project_uid, run_id):
    try:
        logger.info("call /start/{0}/{1}".format(project_uid, run_id))
        return reqHandler.start_agents(project_uid, run_id)
    except Exception as e:
        e_str = "Exception encountered in /start/<path:project_uid>/<path:run_id>:\n"
        logger.exception(e_str + format_exception(e))
        raise e


@app.route("/evaluate/<path:eval_id>")
def evaluate(eval_id):
    try:
        logger.info("call /evaluate/{}".format(eval_id))
        return reqHandler.evalaute(eval_id)
    except Exception as e:
        e_str = "Exception encountered in /evaluate/<path:eval_id>:\n"
        logger.exception(e_str + format_exception(e))
        raise e


@app.route("/drawing/<path:system>")
def get_image(system):
    try:
        image = reqHandler.get_image(system)
        return Response(image.getvalue(), mimetype="image/png")
    except Exception as e:
        e_str = "Exception encountered in /drawing/<path:system>:\n"
        logger.exception(e_str + format_exception(e))
        raise e


@app.route("/postcsv/<path:filetype>", methods=["POST"])
def postCsv(filetype):
    try:
        file = request.files["file"]
        return reqHandler.add_series(filetype, file)
    except Exception as e:
        e_str = "Exception encountered in /postcsv/<path:filetype>:\n"
        logger.exception(e_str + format_exception(e))
        raise e


@app.route("/hydropowersystem/<path:system>")
def get_hydrosystem(system):
    try:
        system = reqHandler.get_system(system)
        return Response(system, mimetype="application/json")
    except Exception as e:
        e_str = "Exception encountered in /hydropowersystem/<path:system>:\n"
        logger.exception(e_str + format_exception(e))
        raise e
