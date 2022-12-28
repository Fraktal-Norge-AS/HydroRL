using System;
using System.ComponentModel;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using Newtonsoft.Json;

namespace DKWebapp.Models.ApiPoco
{
    public abstract class ApiObject
    {
        public string Name { get; set; }
        public string Uid { get; set; }
    }

    public class ApiProject : ApiObject
    {
        public ApiHydroSystem HydroSystem { get; set; }
    }

    public class ApiHydroSystem : ApiObject
    {
        public string Description { get; set; }
    }

    public class ApiReservoir : ApiObject
    {
        public double MinVolume { get; set; }
        public double MaxVolume { get; set; }
    }

    public class ApiForecast : ApiObject
    { 
    }

    public class ApiForecastScenarios
    {
        public List<String> Scenarios { get; set; }
    }

    public class ApiForecastScenario
    {
        public List<DateTimeOffset> TimeIndex { get; set; }
        public List<double> InflowSeries { get; set; }
        public List<double> PriceSeries { get; set; }
    }



    public class ApiRun : ApiObject
    {
        public Nullable<DateTimeOffset> StartTime { get; set; }
        public Nullable<DateTimeOffset> EndTime { get; set; }
        public RunSettings Settings { get; set; }
        public ApiForecast Forecast { get; set; }
    }

    public enum EndStateIncentive{
        MeanEnergyPrice,
        LastEnergyPrice,
        ProvidedEndEnergyPrice,
        Off
        
    }

    public enum Noise{
        StandardDev,
        White,
        Off
    }

    public enum StepResolution{
        Day,
        Week,
        Hour
    }
    public enum AgentAlgorithm{
        SAC,
        A2C,
        DDPG,
        TD3,
        PPO
    }

    public class RunSettings
    {
        [DefaultValue("comment")]
        public string Comment { get; set; }

        [DefaultValue(1000)]
        public int TrainEpisodes { get; set; }

        [DefaultValue(EndStateIncentive.MeanEnergyPrice)]
        [JsonConverter(typeof(Newtonsoft.Json.Converters.StringEnumConverter))]
        public EndStateIncentive EndStateIncentive { get; set; }

        [DefaultValue(Noise.Off)]
        [JsonConverter(typeof(Newtonsoft.Json.Converters.StringEnumConverter))]
        public Noise Noise {get; set;}

        [DefaultValue(null)]
        public string PreviousProjectRunUid { get; set; }

        [DefaultValue(null)]
        public string PreviousQValueProjectRunUid {get; set;}

        [Range(0.0, 0.3, ErrorMessage = "Value for {0} must be between {1} and {2}.")]
        [DefaultValue(0.04)]
        public double DiscountRate { get; set; }
        public Dictionary<String, double> StartVolumes { get; set; }

        [Range(20, 10000, ErrorMessage = "Value for {0} must be between {1} and {2}.")]
        [DefaultValue(52)]
        public int StepsInEpisode { get; set; }

        [DefaultValue(StepResolution.Week)]
        [JsonConverter(typeof(Newtonsoft.Json.Converters.StringEnumConverter))]
        public StepResolution StepResolution {get; set;}

        [Range(1, 7, ErrorMessage = "Value for {0} must be between {1} and {2}.")]
        [DefaultValue(1)]
        public int StepFrequency {get; set;}

        [DefaultValue(true)]
        public bool RandomizeStartVolume {get; set;}

        [Range(0.001, 1000, ErrorMessage = "Value for {0} must be between {1} and {2}.")]
        [DefaultValue(10)]
        public double RewardScaleFactor {get; set;}

        [Range(1, 20, ErrorMessage = "Value for {0} must be between {1} and {2}.")]
        [DefaultValue(7)]
        public int ForecastClusters {get; set;}

        [Range(0, 10, ErrorMessage = "Value for {0} must be between {1} and {2}.")]
        [DefaultValue(1)]
        public double PriceOfSpillage {get; set;}

        [Range(0.0, 3000.0, ErrorMessage = "Value for {0} must be between {1} and {2}.")]
        [DefaultValue(null)]
        public double EndEnergyPrice {get; set;}

        [Range(1, 500, ErrorMessage = "Value for {0} must be between {1} and {2}.")]
        [DefaultValue(5)]
        public int EvaluationEpisodes {get; set;}
        [Range(1, 1000, ErrorMessage = "Value for {0} must be between {1} and {2}.")]
        [DefaultValue(30)]
        public int EvaluationInterval { get; set; }

        [DefaultValue(AgentAlgorithm.SAC)]
        [JsonConverter(typeof(Newtonsoft.Json.Converters.StringEnumConverter))]
        public AgentAlgorithm AgentAlgorithm { get; set; }
    }



    public class ApiTimeSeries{
        public string Name { get; set; }
        public List<double> Values{ get; set; }
    }

    public class ApiReportEpisode{
        public string Name { get; set; }
        public List<ApiTimeSeries> Series { get; set; }
    }

    public class ApiReportData{
        public List<ApiReportEpisode> Episodes { get; set; }
        public List<DateTimeOffset> TimeStamps{ get; set; }        
    }

    public class RunDetails{
        public double Progress { get; set; }
        public List<ApiStepSeries> Status  {get; set; }
    }

    public class ApiStepSeries{
        public string Name { get; set; }
        public List<double> Steps{ get; set; }
        public List<double> Values{ get; set; }
    }
}