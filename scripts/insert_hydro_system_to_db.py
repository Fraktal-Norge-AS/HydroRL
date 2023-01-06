#%% 
import sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from datetime import datetime
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc

from server.model import Forecast, Project, ProjectRun, ProjectRunStartVolume, SeriesLink, TimeDataValue, TimeDataSery, EvaluationEpisode, ReportDatum, ReportValue, Agent
from server.appsettings import appSettings

#%%
from server.model import Reservoir, HydroSystem
from hydro_systems import HSGen
from uuid import uuid4

start_volume = {
    "small": {
        "res1": 0
    },
    "medium": {
        "res1": 0,
        "res2": 0,
        "res3": 0
    },
    "large": {
        "res1": 0,
        "res2": 0,
        "res3": 0,
        "res4": 0,
        "res5": 0,
        "res6": 0,
        "res7": 0,
        "res8": 0
        
    },
}

def add_reservoirs_to_db(hydro_systems):
    for hs in hydro_systems:
        if session.query(HydroSystem).filter(HydroSystem.Name == hs).first() is None:
            uuid = uuid4()
            hs_add = HydroSystem(
                Name = hs,
                Description = "Representasjonen av hydrosystemet " + hs,
                HydroSystemUid = str(uuid)
            )
            session.add(hs_add)
            session.flush()

        hs_gen = HSGen.create_system(name=hs, start_volume=start_volume[hs], price_of_spillage=1, use_linear_model=False)
        
        for res in hs_gen.reservoirs:
            if not res.is_ocean:
                hydro_system_id = session.query(HydroSystem).filter(HydroSystem.Name == hs).first().HydroSystemId
                if session.query(Reservoir).filter(Reservoir.HydroSystemId == hydro_system_id, Reservoir.Name == res.name).first() is None:
                    res_add = Reservoir(
                        ReservoirUid=str(uuid4()),
                        HydroSystemId=hydro_system_id,
                        Name=res.name,
                        MinVolume=res.min_volume,
                        MaxVolume=res.max_volume
                    )
                    session.add(res_add)
                    session.flush()

        session.commit()


#%% Add Start volume to db

def upload_initial_reservoir_value(hydro_systems, prct: int):
    try:
        for hs in hydro_systems:
            hs_gen = HSGen.create_system(name=hs, start_volume=start_volume[hs], price_of_spillage=1, use_linear_model=False)
            hydro_system_id = session.query(HydroSystem).filter(HydroSystem.Name == hs).first().HydroSystemId

            project = session.query(Project).filter(Project.Name == f"ConsoleProject {prct}% volume " + hs).first()
            if project is None:
                proj = Project(
                    ProjectUid=str(uuid4()),
                    Name=f"ConsoleProject {prct}% volume " + hs,
                    HydroSystemId=hydro_system_id
                )
                session.add(proj)
                session.flush()
                
                proj_run = ProjectRun(
                    ProjectRunGuid=str(uuid4()),
                    ProjectId=proj.ProjectId,
                    StartTime=datetime.now(),
                    ForecastId=0,
                    Comment="Console run. No logging to db."
                )
                session.add(proj_run)
                session.flush()
            else:
                proj_run = session.query(ProjectRun).filter(ProjectRun.ProjectId == project.ProjectId).first()
            for res in hs_gen.reservoirs:
                if not res.is_ocean:
                    reservoir_id = session.query(Reservoir).filter(Reservoir.HydroSystemId == hydro_system_id, Reservoir.Name == res.name).first().ReservoirId
                    start_vol_add = ProjectRunStartVolume(
                            ProjectRunId=proj_run.ProjectRunId,
                            ReservoirId=reservoir_id,
                            Value=res.max_volume * prct/100
                        )
                    session.add(start_vol_add)
                    session.flush()

        session.commit()

    except exc.SQLAlchemyError as e:
        session.rollback()
        raise(e)

connection_string = appSettings.get_connection_string()
engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)
session = Session()

hydro_systems = ["small", "medium", "large"]
add_reservoirs_to_db(hydro_systems)
# upload_initial_reservoir_value(hydro_systems, 15)
