import sys
from pathlib import Path

sys.path.insert(0, str(Path.home()/Path("gitsource/HydroScheduling")))
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from server.model import Forecast, SeriesLink, HydroSystem
from server.appsettings import appSettings
import uuid

connection_string = appSettings.get_connection_string()

engine = create_engine(connection_string, connect_args={'timeout': 15})
Session = sessionmaker(bind=engine)
session = Session()

existing_hydro_systems = session.query(HydroSystem).all()
fc = session.query(Forecast).first()

for hs in existing_hydro_systems:
    det_price = Forecast(UploadId=fc.UploadId, ForecastUid=str(uuid.uuid4()), HydroSystemId=hs.HydroSystemId, Name="det_price_" + hs.Name)
    det_inflow = Forecast(UploadId=fc.UploadId, ForecastUid=str(uuid.uuid4()), HydroSystemId=hs.HydroSystemId, Name="det_inflow_" + hs.Name)

    session.add(det_inflow)
    session.add(det_price)
    session.commit()
    session.flush()

    from_links = session.query(SeriesLink).filter_by(ForecastId=fc.ForecastId).all()

    pick_link = from_links[0]
    pick_price_id = pick_link.PriceSeriesId
    pick_inflow_id = pick_link.InflowSeriesId

    for link in from_links:
        price_link = SeriesLink(UploadId=link.UploadId, ForecastId=det_price.ForecastId, InflowSeriesId=link.InflowSeriesId, PriceSeriesId=pick_price_id)
        inflow_link = SeriesLink(UploadId=link.UploadId, ForecastId=det_inflow.ForecastId, InflowSeriesId=pick_inflow_id, PriceSeriesId=link.PriceSeriesId)
        session.add(price_link)
        session.add(inflow_link)
    
    session.commit()