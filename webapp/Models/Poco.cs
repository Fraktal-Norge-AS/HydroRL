using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using Newtonsoft.Json;

namespace DKWebapp.Models
{
    public class Project
    {
        public int ProjectId { get; set; }
        public string ProjectUid { get; set; }
        public string Name { get; set; }
        public int HydroSystemId { get; set; }
        public HydroSystem HydroSystem { get; set; }
    }

    public class HydroSystem
    {
        public int HydroSystemId { get; set; }
        public string HydroSystemUid { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public ICollection<Reservoir> Reservoirs { get; set; }
    }

    public class Reservoir
    {
        public int ReservoirId { get; set; }
        public string ReservoirUid { get; set; }
        public int HydroSystemId { get; set; }
        [JsonIgnore]
        public HydroSystem HydroSystem { get; set; }
        public string Name { get; set; }
        public double MinVolume { get; set; }
        public double MaxVolume { get; set; }
    }

    public class EvaluationEpisode
    {
        public int EvaluationEpisodeId { get; set; }
        public int ProjectRunId { get; set; }
        public ProjectRun ProjectRun { get; set; }
        public string Description { get; set; }
        public ICollection<ReportSeries> Series { get; set; }
        public int AgentId { get; set; }
        public Agent Agent { get; set; }
    }

    public class ProjectRun
    {
        public int ProjectRunId { get; set; }
        public string ProjectRunGuid { get; set; }
        public int ProjectId { get; set; }
        public Project Project { get; set; }
        public Nullable<DateTimeOffset> StartTime { get; set; }
        public Nullable<DateTimeOffset> EndTime { get; set; }
        public int ForecastId { get; set; }
        public Forecast Forecast { get; set; }
        public string Settings { get; set; }
        public string ApiSettings { get; set; }
        public string Comment { get; set; }
        [ForeignKey("Agent")]
        public int? EvaluatedOn { get; set; }
        public Agent Agent { get; set; }
        [ForeignKey("ProjectRun")]
        public int? PreviousProjectRunId {get; set;}
        public ProjectRun PreviousProjectRun {get; set;}
        [ForeignKey("ProjectRun")]
        public int? PreviousQValueProjectRunId {get; set;}
        public ProjectRun PreviousQValueProjectRun {get; set;}
    }

    public class ProjectRunStartVolume
    {
        public int ProjectRunStartVolumeId { get; set; }
        public int ProjectRunId { get; set; }
        public ProjectRun ProjectRun { get; set; }
        public int ReservoirId { get; set; }
        public Reservoir Reservoir { get; set; }
        public double Value { get; set; }
    }

    public class Agent
    {
        public int AgentId { get; set; }
        public string AgentUid { get; set; }
        public int ProjectId { get; set; }
        public Project Project { get; set; }
        public int ProjectRunId { get; set; }
        public ProjectRun ProjectRun { get; set; }
        public int Seed { get; set; }
        public string BestModelPath { get; set; }
        public DateTimeOffset StartTime { get; set; }
        public Nullable<DateTimeOffset> EndTime { get; set; }
        public Nullable<int> Ancestor { get; set; }
        public Nullable<int> BestStep { get; set; }
        public Nullable<double> BestStepValue { get; set; }
    }

    public class AgentSeriesValue
    {
        public Agent A { get; set; }
        public StepSeries S { get; set; }
        public StepValue V { get; set; }
        public Project P { get; set; }
        public ProjectRun R { get; set; }
    }

    public class AgentControl
    {
        public int AgentControlId { get; set; }
        public int AgentId { get; set; }
        public Agent Agent { get; set; }
        public Nullable<int> Signal { get; set; }
    }

    public enum ProjectRunSignal
    {
        Terminate = 0,
        SpawnBestWithBuffer = 1,
        SpawnBestNoBuffer = 2
    }

    public class ProjectRunControl
    {
        public int ProjectRunControlId { get; set; }
        public int ProjectRunId { get; set; }
        public ProjectRun ProjectRun { get; set; }
        public Nullable<ProjectRunSignal> Signal { get; set; }
    }

    public class Series
    {
        public DateTimeOffset StartTime { get; set; }
        public Nullable<DateTimeOffset> EndTime { get; set; }
        public string Description { get; set; }
        public string Type { get; set; }
    }

    public class ReportSeries : Series
    {
        public int EvaluationEpisodeId { get; set; }
        [JsonIgnore]
        public EvaluationEpisode EvaluationEpisode { get; set; }
        public int ReportSeriesId { get; set; }
        public ICollection<ReportValue> Values { get; set; }
    }

    public class ReportValue
    {
        public int ReportSeriesId { get; set; }
        [JsonIgnore]
        public ReportSeries ReportSeries { get; set; }
        public int Step { get; set; }
        public int Index { get; set; }
        public DateTimeOffset TimeStamp { get; set; }
        public double Value { get; set; }
    }

    public class StepSeries : Series
    {
        public int AgentId { get; set; }
        [JsonIgnore]
        public Agent Agent { get; set; }
        public int StepSeriesId { get; set; }
        public ICollection<StepValue> Values { get; set; }
    }

    public class StepValue
    {
        public int StepSeriesId { get; set; }
        [JsonIgnore]
        public StepSeries StepSeries { get; set; }
        public int Step { get; set; }
        public DateTimeOffset TimeStamp { get; set; }
        public double Value { get; set; }
    }

    public enum TimeDataSeriesType
    {
        Inflow,
        Price
    }

    public class Upload
    {
        public int UploadId { get; set; }
        public DateTimeOffset UploadTime { get; set; }
        public string SourceFile { get; set; }
        public List<TimeDataSeries> Series { get; set; }
    }

    public class Forecast
    {
        public int ForecastId { get; set; }
        public string ForecastUid { get; set; }
        public int UploadId { get; set; }
        public Upload Upload { get; set; }
        public int HydroSystemId { get; set; }
        public HydroSystem HydroSystem { get; set; }
        public string Name { get; set; }
        public List<TimeDataSeriesLink> SeriesLinks { get; set; }
    }

    public class TimeDataSeriesLink
    {
        public int UploadId { get; set; }
        public Upload Upload { get; set; }
        public int ForecastId { get; set; }
        public Forecast Forecast { get; set; }
        public int TimeDataSeriesLinkId { get; set; }
        [ForeignKey("TimeDataSeries")]
        public int InflowSeriesId { get; set; }
        [ForeignKey("TimeDataSeries")]
        public int PriceSeriesId { get; set; }
    }

    public class TimeDataSeries
    {
        public int TimeDataSeriesId { get; set; }
        public int UploadId { get; set; }
        public Upload Upload { get; set; }
        public DateTimeOffset StartTime { get; set; }
        public DateTimeOffset EndTime { get; set; }
        public string Description { get; set; }
        public TimeDataSeriesType Type { get; set; }
        public List<TimeDataValue> Values { get; set; }
    }

    public class TimeDataValue
    {
        public int TimeDataSeriesId { get; set; }
        public TimeDataSeries TimeDataSeries { get; set; }
        public DateTimeOffset TimeStampOffset { get; set; }
        public double Value { get; set; }
    }

    public class PresentationData
    {
        public string Name { get; set; }
        public List<TimeDataValue> Values { get; set; }
    }

    public class PresentationSeries
    {
        public PresentationData Inflow { get; set; }
        public PresentationData Price { get; set; }
    }
}

