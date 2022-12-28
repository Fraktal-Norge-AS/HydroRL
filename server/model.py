# coding: utf-8
from sqlalchemy import Column, Float, ForeignKey, Integer, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class HydroSystem(Base):
    __tablename__ = "HydroSystems"

    HydroSystemId = Column(Integer, primary_key=True)
    HydroSystemUid = Column(Text)
    Name = Column(Text)
    Description = Column(Text)


class Upload(Base):
    __tablename__ = "Uploads"

    UploadId = Column(Integer, primary_key=True)
    UploadTime = Column(Text, nullable=False)
    SourceFile = Column(Text)


class EFMigrationsHistory(Base):
    __tablename__ = "__EFMigrationsHistory"

    MigrationId = Column(Text, primary_key=True)
    ProductVersion = Column(Text, nullable=False)


t_sqlite_sequence = Table("sqlite_sequence", metadata, Column("name", NullType), Column("seq", NullType))


class Forecast(Base):
    __tablename__ = "Forecasts"

    ForecastId = Column(Integer, primary_key=True)
    ForecastUid = Column(Text)
    UploadId = Column(ForeignKey("Uploads.UploadId", ondelete="CASCADE"), nullable=False, index=True)
    HydroSystemId = Column(ForeignKey("HydroSystems.HydroSystemId", ondelete="CASCADE"), nullable=False, index=True)
    Name = Column(Text)

    HydroSystem = relationship("HydroSystem")
    Upload = relationship("Upload")


class Project(Base):
    __tablename__ = "Projects"

    ProjectId = Column(Integer, primary_key=True)
    ProjectUid = Column(Text)
    Name = Column(Text, unique=True)
    HydroSystemId = Column(ForeignKey("HydroSystems.HydroSystemId", ondelete="CASCADE"), nullable=False, index=True)

    HydroSystem = relationship("HydroSystem")


class Reservoir(Base):
    __tablename__ = "Reservoirs"

    ReservoirId = Column(Integer, primary_key=True)
    ReservoirUid = Column(Text)
    HydroSystemId = Column(ForeignKey("HydroSystems.HydroSystemId", ondelete="CASCADE"), nullable=False, index=True)
    Name = Column(Text)
    MinVolume = Column(Float, nullable=False)
    MaxVolume = Column(Float, nullable=False)

    HydroSystem = relationship("HydroSystem")


class TimeDataSery(Base):
    __tablename__ = "TimeDataSeries"

    TimeDataSeriesId = Column(Integer, primary_key=True)
    UploadId = Column(ForeignKey("Uploads.UploadId", ondelete="CASCADE"), nullable=False, index=True)
    StartTime = Column(Text, nullable=False)
    EndTime = Column(Text, nullable=False)
    Description = Column(Text)
    Type = Column(Integer, nullable=False)

    Upload = relationship("Upload")


class Agent(Base):
    __tablename__ = "Agents"

    AgentId = Column(Integer, primary_key=True)
    AgentUid = Column(Text)
    ProjectId = Column(ForeignKey("Projects.ProjectId", ondelete="CASCADE"), nullable=False, index=True)
    ProjectRunId = Column(ForeignKey("ProjectRuns.ProjectRunId", ondelete="CASCADE"), nullable=False, index=True)
    Seed = Column(Integer, nullable=False)
    BestModelPath = Column(Text)
    StartTime = Column(Text, nullable=False)
    EndTime = Column(Text)
    Ancestor = Column(Integer)
    BestStep = Column(Integer)
    BestStepValue = Column(Float)

    Project = relationship("Project")
    ProjectRun = relationship("ProjectRun", primaryjoin="Agent.ProjectRunId == ProjectRun.ProjectRunId")


class SeriesLink(Base):
    __tablename__ = "SeriesLinks"

    TimeDataSeriesLinkId = Column(Integer, primary_key=True)
    UploadId = Column(ForeignKey("Uploads.UploadId", ondelete="CASCADE"), nullable=False, index=True)
    ForecastId = Column(ForeignKey("Forecasts.ForecastId", ondelete="CASCADE"), nullable=False, index=True)
    InflowSeriesId = Column(Integer, nullable=False)
    PriceSeriesId = Column(Integer, nullable=False)

    Forecast = relationship("Forecast")
    Upload = relationship("Upload")


class TimeDataValue(Base):
    __tablename__ = "TimeDataValue"

    TimeDataSeriesId = Column(
        ForeignKey("TimeDataSeries.TimeDataSeriesId", ondelete="CASCADE"), primary_key=True, nullable=False
    )
    TimeStampOffset = Column(Text, primary_key=True, nullable=False)
    Value = Column(Float, nullable=False)

    TimeDataSery = relationship("TimeDataSery")


class AgentControl(Base):
    __tablename__ = "AgentControls"

    AgentControlId = Column(Integer, primary_key=True)
    AgentId = Column(ForeignKey("Agents.AgentId", ondelete="CASCADE"), nullable=False, index=True)
    Signal = Column(Integer)

    Agent = relationship("Agent")


class ProjectRun(Base):
    __tablename__ = "ProjectRuns"

    ProjectRunId = Column(Integer, primary_key=True)
    ProjectRunGuid = Column(Text)
    ProjectId = Column(ForeignKey("Projects.ProjectId", ondelete="CASCADE"), nullable=False, index=True)
    StartTime = Column(Text)
    EndTime = Column(Text)
    ForecastId = Column(ForeignKey("Forecasts.ForecastId", ondelete="CASCADE"), nullable=False, index=True)
    Settings = Column(Text)
    ApiSettings = Column(Text)
    Comment = Column(Text)
    EvaluatedOn = Column(ForeignKey("Agents.AgentId", ondelete="RESTRICT"), index=True)
    PreviousProjectRunId = Column(ForeignKey("ProjectRuns.ProjectRunId", ondelete="RESTRICT"), index=True)
    PreviousQValueProjectRunId = Column(ForeignKey("ProjectRuns.ProjectRunId", ondelete="RESTRICT"), index=True)

    Agent = relationship("Agent", primaryjoin="ProjectRun.EvaluatedOn == Agent.AgentId")
    Forecast = relationship("Forecast")
    parent = relationship(
        "ProjectRun",
        remote_side=[ProjectRunId],
        primaryjoin="ProjectRun.PreviousProjectRunId == ProjectRun.ProjectRunId",
    )
    parent1 = relationship(
        "ProjectRun",
        remote_side=[ProjectRunId],
        primaryjoin="ProjectRun.PreviousQValueProjectRunId == ProjectRun.ProjectRunId",
    )
    Project = relationship("Project")


class StepDatum(Base):
    __tablename__ = "TrainStepData"

    StepSeriesId = Column(Integer, primary_key=True)
    StartTime = Column(Text, nullable=False)
    EndTime = Column(Text)
    Description = Column(Text)
    Type = Column(Text)
    AgentId = Column(ForeignKey("Agents.AgentId", ondelete="CASCADE"), nullable=False, index=True)

    Agent = relationship("Agent")


class EvaluationEpisode(Base):
    __tablename__ = "EvaluationEpisodes"

    EvaluationEpisodeId = Column(Integer, primary_key=True)
    ProjectRunId = Column(ForeignKey("ProjectRuns.ProjectRunId", ondelete="CASCADE"), nullable=False, index=True)
    Description = Column(Text)
    AgentId = Column(ForeignKey("Agents.AgentId", ondelete="CASCADE"), nullable=False, index=True)

    Agent = relationship("Agent")
    ProjectRun = relationship("ProjectRun")


class ProjectRunControl(Base):
    __tablename__ = "ProjectRunControls"

    ProjectRunControlId = Column(Integer, primary_key=True)
    ProjectRunId = Column(ForeignKey("ProjectRuns.ProjectRunId", ondelete="CASCADE"), nullable=False, index=True)
    Signal = Column(Integer)

    ProjectRun = relationship("ProjectRun")


class ProjectRunStartVolume(Base):
    __tablename__ = "ProjectRunStartVolume"

    ProjectRunStartVolumeId = Column(Integer, primary_key=True)
    ProjectRunId = Column(ForeignKey("ProjectRuns.ProjectRunId", ondelete="CASCADE"), nullable=False, index=True)
    ReservoirId = Column(ForeignKey("Reservoirs.ReservoirId", ondelete="CASCADE"), nullable=False, index=True)
    Value = Column(Float, nullable=False)

    ProjectRun = relationship("ProjectRun")
    Reservoir = relationship("Reservoir")


class StepValue(Base):
    __tablename__ = "TrainStepValues"

    StepSeriesId = Column(
        ForeignKey("TrainStepData.StepSeriesId", ondelete="CASCADE"), primary_key=True, nullable=False
    )
    Step = Column(Integer, primary_key=True, nullable=False)
    TimeStamp = Column(Text, nullable=False)
    Value = Column(Float, nullable=False)

    TrainStepDatum = relationship("StepDatum")


class ReportDatum(Base):
    __tablename__ = "ReportData"

    ReportSeriesId = Column(Integer, primary_key=True)
    StartTime = Column(Text, nullable=False)
    EndTime = Column(Text)
    Description = Column(Text)
    Type = Column(Text)
    EvaluationEpisodeId = Column(
        ForeignKey("EvaluationEpisodes.EvaluationEpisodeId", ondelete="CASCADE"), nullable=False, index=True
    )

    EvaluationEpisode = relationship("EvaluationEpisode")


class ReportValue(Base):
    __tablename__ = "ReportValues"

    ReportSeriesId = Column(
        ForeignKey("ReportData.ReportSeriesId", ondelete="CASCADE"), primary_key=True, nullable=False
    )
    Step = Column(Integer, primary_key=True, nullable=False)
    Index = Column(Integer, primary_key=True, nullable=False)
    TimeStamp = Column(Text, nullable=False)
    Value = Column(Float, nullable=False)

    ReportDatum = relationship("ReportDatum")
