using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using DKWebapp.Models;
using System.IO;

namespace DKWebapp.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    [ApiExplorerSettings(IgnoreApi=true)]
    public class SeriesController : ControllerBase
    {
        private readonly ProjectContext _context;

        public SeriesController(ProjectContext context)
        {
            _context = context;
        }

        [HttpGet("/api/stepseries")]
        public async Task<ActionResult<IEnumerable<StepSeries>>> GetStepSeries()
        {
            return await _context.TrainStepData.ToListAsync();
        }

        [HttpGet("/api/agentseries/{runid}/{filter}")]
        public ActionResult<List<StepSeries>> GetAgentSeries(int runid, string filter, DateTime after)
        {
            var result =
                from prjrun in _context.ProjectRuns
                join agent in _context.Agents
                on prjrun.ProjectRunId equals agent.ProjectRunId
                join series in _context.TrainStepData
                on agent.AgentId equals series.AgentId
                where series.Type == filter && prjrun.ProjectRunId == runid 
                select series;

            return result.ToList();
        }


        [HttpGet("/api/agentdata/{runid}/{filter}/{after}")]
        public ActionResult<List<StepValue>> GetAgentData(int runid, string filter, DateTime after)
        {
            var result =
                from prjrun in _context.ProjectRuns
                join agent in _context.Agents
                on prjrun.ProjectRunId equals agent.ProjectRunId
                join series in _context.TrainStepData
                on agent.AgentId equals series.AgentId
                join data in _context.TrainStepValues
                on series.StepSeriesId equals data.StepSeriesId
                where prjrun.ProjectRunId == runid && data.TimeStamp > after
                select data;

            return result.ToList();
        }


        [HttpGet("/api/forecast_data/{forecastId}")]
        public ActionResult<List<PresentationSeries>> GetForecastData(int forecastId)
        {
            List<TimeDataSeriesLink> links = _context.SeriesLinks.Where(a => a.ForecastId == forecastId).ToList();

            List<PresentationSeries> result = new List<PresentationSeries>();
            foreach(var link in links)
            {
                var inflow = _context.TimeDataValue.FromSql("SELECT * from TimeDataValue where TimeDataSeriesId = {0} and ROWID % 25 = 0", link.InflowSeriesId).ToList();
                var price = _context.TimeDataValue.FromSql("SELECT * from TimeDataValue where TimeDataSeriesId = {0} and ROWID % 25 = 0", link.PriceSeriesId).ToList();

                PresentationData pdata = new PresentationData(){ Name = "price", Values = price };
                PresentationData idata = new PresentationData(){ Name = "inflow", Values = inflow };

                result.Add(new PresentationSeries(){ Inflow = idata, Price = pdata});
            }
            return result;
        }

        [HttpGet("/api/plots/{relationId}/{type}/{step}")]
        public ActionResult<List<ReportSeries>> GetPlots(int relationId, string type, int step)
        {   
            var data = from p in _context.ReportData
            join eval in _context.EvaluationEpisodes on p.EvaluationEpisodeId equals eval.EvaluationEpisodeId
            where eval.AgentId == relationId 
            select new {
                Parent = p,
                Values = from c in _context.ReportValues
                where c.Step == step && c.ReportSeriesId == p.ReportSeriesId
                select c
            };

            List<ReportSeries> result = new List<ReportSeries>();
            foreach (var d in data)
            {
                ReportSeries s = d.Parent;
                s.Values = d.Values.ToList();
                result.Add(s);
            }
            return result;
        }

        [HttpGet("/api/eval_episodes/{evaluation_id}")]
        public ActionResult<List<EvaluationEpisode>> GetEvalEpisodes(int evaluation_id){
            return (from ee in _context.EvaluationEpisodes
                where ee.ProjectRunId == evaluation_id
                select ee).ToList();
        }

    }
}
