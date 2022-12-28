from sqlalchemy import desc
from server.db_connection import create_engine

from sqlalchemy.orm import sessionmaker, joinedload

from model import Project, Agent, ProjectRun, HydroSystem, Reservoir
from appsettings import appSettings


class ProjectStatus:
    def __init__(self, projectGuid):
        self.engine = create_engine()
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.project = self.session.query(Project).filter_by(ProjectUid=projectGuid).first()
        self.hydro_system = self.session.query(HydroSystem).get(self.project.HydroSystemId)

    def get_start_folder(self, agent_id):
        agent = self.session.query(Agent).filter_by(AgentId=agent_id).first()
        if agent is None:
            return None
        return agent.BestModelPath

    def get_start_volumes(self):
        reservoirs = self.session.query(Reservoir).filter_by(HydroSystemId=self.project.HydroSystemId).all()

        result = {}
        for r in reservoirs:
            result[r.Name] = r.MaxVolume / 2

        return result

    def is_running(self, run_id):
        run = self.session.query(ProjectRun).filter_by(ProjectRunId=run_id).first()

        if run is None:
            raise ValueError("Invalid run " + str(run_id))

        return run.StartTime is not None
