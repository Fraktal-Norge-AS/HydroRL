using System;
using System.Collections.Generic;
using Newtonsoft.Json;
using DKWebapp.Models.ApiPoco;

namespace DKWebapp.Models
{
    public static class PocoConverter
    {
        public static ApiReportData Convert(IEnumerable<ReportValue> reportValues)
        {
            Dictionary<string, EvaluationEpisode> lookup = new Dictionary<string, EvaluationEpisode>();
            foreach( var value in reportValues){
                string name = value.ReportSeries.EvaluationEpisode.Description;
                if(!lookup.ContainsKey(name))
                    lookup.Add(name, value.ReportSeries.EvaluationEpisode);
            }

            ApiReportData result = new ApiReportData(){ TimeStamps = null, Episodes = new List<ApiReportEpisode>()};
            foreach( var eval in lookup.Values)
            {
                ApiReportEpisode episode = new ApiReportEpisode(){Name = eval.Description, Series = new List<ApiTimeSeries>() };
                result.Episodes.Add(episode);

                foreach(var series in eval.Series){
                    ApiTimeSeries apiSeries = new ApiTimeSeries(){ Name = series.Description, Values = new List<double>()};
                    episode.Series.Add(apiSeries);

                    foreach (var val in series.Values)
                        apiSeries.Values.Add(val.Value);

                    if (result.TimeStamps == null){
                        result.TimeStamps = new List<DateTimeOffset>();
                        foreach (var val in series.Values)
                            result.TimeStamps.Add(val.TimeStamp);
                    }
                }
            }
            return result;
        }


        public static List<ApiRun> Convert(IEnumerable<ProjectRun> projectRuns)
        {
            List<ApiRun> result = new List<ApiRun>();
            foreach (var p in projectRuns)
                result.Add(Convert(p));
            return result;
        }

        public static List<ApiProject> Convert(IEnumerable<Project> projects)
        {
            List<ApiProject> result = new List<ApiProject>();
            foreach (var p in projects)
                result.Add(Convert(p));
            return result;
        }

        public static List<ApiHydroSystem> Convert(IEnumerable<HydroSystem> systems)
        {
            List<ApiHydroSystem> result = new List<ApiHydroSystem>();
            foreach (var s in systems)
                result.Add(Convert(s));
            return result;
        }

        public static List<ApiReservoir> Convert(IEnumerable<Reservoir> reservoirs)
        {
            List<ApiReservoir> result = new List<ApiReservoir>();
            foreach (var r in reservoirs)
                result.Add(Convert(r));
            return result;
        }

        public static List<ApiForecast> Convert(IEnumerable<Forecast> forecasts)
        {
            List<ApiForecast> result = new List<ApiForecast>();
            foreach (var f in forecasts)
                result.Add(Convert(f));
            return result;
        }

        public static ApiProject Convert(Project p)
        {
            return new ApiProject { Name = p.Name, Uid = p.ProjectUid, HydroSystem = Convert(p.HydroSystem) };
        }

        public static ApiForecast Convert(Forecast f)
        {
            return new ApiForecast { Name = f.Name, Uid = f.ForecastUid };
        }

        public static ApiHydroSystem Convert(HydroSystem h)
        {
            return new ApiHydroSystem { Name = h.Name, Uid = h.HydroSystemUid, Description = h.Description };
        }

        public static ApiReservoir Convert(Reservoir r)
        {
            return new ApiReservoir { Name = r.Name, Uid = r.ReservoirUid, MaxVolume = r.MaxVolume, MinVolume = r.MinVolume };
        }

        public static ApiRun Convert(ProjectRun r)
        {
            var run = new ApiRun { Name = r.Comment, Uid = r.ProjectRunGuid, StartTime = r.StartTime, EndTime = r.EndTime, Forecast = Convert(r.Forecast) };
            run.Settings = r.ApiSettings == null ? null : JsonConvert.DeserializeObject<RunSettings>(r.ApiSettings);
            return run;
        }

        public static RunDetails Convert(List<StepSeries> series)
        {
            var result = new RunDetails { Progress = 100.0, Status = new List<ApiStepSeries>() };

            foreach (var sery in series)
            {
                var steps = new List<double>(sery.Values.Count);
                var values = new List<double>(sery.Values.Count);

                foreach (var point in sery.Values)
                {
                    steps.Add(point.Step);
                    values.Add(point.Value);
                }
                result.Status.Add(new ApiStepSeries { Values = values, Steps = steps, Name = sery.Description });
            }
            return result;
        }        
    }
}