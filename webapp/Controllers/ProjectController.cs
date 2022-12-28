using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using DKWebapp.Models;
using Newtonsoft.Json.Linq;

namespace DKWebapp.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    [ApiExplorerSettings(IgnoreApi=true)]
    public class ProjectsController : ControllerBase
    {
        private readonly ProjectContext _context;

        public ProjectsController(ProjectContext context)
        {
            _context = context;
        }

        // GET: api/Projects
        [HttpGet]
        public async Task<ActionResult<IEnumerable<Project>>> GetProjects()
        {
            return await _context.Projects.Include(a => a.HydroSystem).ToListAsync();
        }

        // GET: api/Projects/5
        [HttpGet("{id}")]
        public ActionResult<Project> GetProject(string id)
        {
            var project = _context.Projects.Where(p => p.ProjectUid == id).Include(a => a.HydroSystem).FirstOrDefault();

            if (project == null) return NotFound();
            return project;
        }

        // POST: api/Projects
        [HttpPost]
        public async Task<ActionResult<Project>> PostProject(Project project)
        {
            project.ProjectUid = Guid.NewGuid().ToString("N");
            _context.Projects.Add(project);
            await _context.SaveChangesAsync();

            return CreatedAtAction("PostProject", new { id = project.ProjectUid }, project);
        }

        // POST: api/Projects
        [HttpPost("/api/add_evalaution")]
        public async Task<ActionResult<ProjectRun>> PostEvaluation([FromBody] ProjectRun evalaution)
        {
            _context.ProjectRuns.Add(evalaution);
            await _context.SaveChangesAsync();

            return evalaution;
        }

        [HttpGet("/api/evalaution/{evalId}")]
        public ActionResult<ProjectRun> GetEvaluation(int evalId)
        {
            return _context.ProjectRuns.Where(e => e.ProjectRunId == evalId).FirstOrDefault();
        }


        // POST: api/ProjectsRun/projectuid + settings
        [HttpPost("/api/pojectrun/{projectUid}/{forecastId}")]
        public async Task<ActionResult<ProjectRun>> PostProjectRun(string projectUid, int forecastId, [FromBody] JObject settings)
        {
            var project = _context.Projects.Where(p => p.ProjectUid == projectUid).Include(p => p.HydroSystem).ThenInclude(h => h.Reservoirs).FirstOrDefault();

            JToken commentToken = null;
            string comment = null;
            if(settings.TryGetValue("run_name", out commentToken))
                comment = commentToken.ToString();

            ProjectRun newRun = new ProjectRun(){ Settings = settings.ToString(), ProjectId = project.ProjectId, Comment = comment, ForecastId = forecastId };
            newRun.ProjectRunGuid = System.Guid.NewGuid().ToString("D");
            _context.Add(newRun);
            await _context.SaveChangesAsync();

            var start_vols = settings.SelectToken("__RunSettings__.start_volumes").ToObject<Dictionary<string, double>>();

            foreach(var res in project.HydroSystem.Reservoirs){
                _context.Add(new ProjectRunStartVolume(){ReservoirId = res.ReservoirId, ProjectRunId = newRun.ProjectRunId, Value=start_vols[res.Name] });
            }
            await _context.SaveChangesAsync();

            return CreatedAtAction("PostProjectRun", newRun);
        }

        [HttpGet("/api/getrun/{project}/{runId}")]
        public ActionResult<ProjectRun> GetCurrentRun(string project, int runId)
        {
            return _context.ProjectRuns.Where(r => r.ProjectRunId == runId).Include(r => r.Forecast).First();
        }

        [HttpGet("/api/currentrun/{project}")]
        public ActionResult<ProjectRun> GetCurrentRun(string project)
        {
            var result =
                (from prj in _context.Projects
                join run in _context.ProjectRuns
                on prj.ProjectId equals run.ProjectId
                where prj.ProjectUid == project && run.EndTime == null
                select run).Include(r => r.Forecast).LastOrDefault();

            return result;
        }

        [HttpGet("/api/runs/{project}")]
        public ActionResult<List<ProjectRun>> GetAllRuns(string project)
        {
            var result =
                (from prj in _context.Projects
                join run in _context.ProjectRuns
                on prj.ProjectId equals run.ProjectId
                where prj.ProjectUid == project
                select run).Include(r => r.Forecast).ToList();

            return result;
        }

        [HttpGet("/api/forecasts/{systemId}")]
        public ActionResult<List<Forecast>> GetForecasts(int systemId)
        {
            return (from f in _context.Forecasts where f.HydroSystemId == systemId select f).ToList();
        }

        [HttpGet("/api/hydro_systems")]
        public ActionResult<List<HydroSystem>> GetHydroSystems()
        {
            return _context.HydroSystems.ToList();
        }

        [HttpGet("/api/agents/{projectrun}")]
        public ActionResult<List<Agent>> GetAgents(int projectrun)
        {
            var result =
                from prjrun in _context.ProjectRuns
                join agent in _context.Agents
                on prjrun.ProjectRunId equals agent.ProjectRunId
                where prjrun.ProjectRunId == projectrun 
                select agent;

            return result.ToList();
        }

        [HttpGet("/api/runs_for_system/{systemId}")]
        public ActionResult GetRunsForSystem(int systemId)
        {
            var res = (from agent in _context.Agents
                    join data in _context.TrainStepData on agent.AgentId equals data.AgentId
                    join run in _context.ProjectRuns on agent.ProjectRunId equals run.ProjectRunId
                    join proj in _context.Projects on run.ProjectId equals proj.ProjectId
                    where data.Description == "Best return" && proj.HydroSystemId == systemId
                    select new {agent = agent, data = data, run = run, proj=proj}).ToList();

            
            Dictionary<int, AgentSeriesValue> result = new Dictionary<int, AgentSeriesValue>();
            foreach(var r in res)
            {
                var sub = (from v in _context.TrainStepValues
                      where v.StepSeriesId == r.data.StepSeriesId
                      orderby v.TimeStamp descending
                      select v).FirstOrDefault();

                int dic_id = r.run.ProjectRunId;

                if(sub != null){
                    if(!result.ContainsKey(dic_id))
                        result.Add(dic_id, new AgentSeriesValue{A = r.agent, S = r.data, V=sub, P=r.proj, R=r.run });
                    else if(result[dic_id].V.Value < sub.Value)
                        result[dic_id] = new AgentSeriesValue{A = r.agent, S = r.data, V=sub, P=r.proj, R=r.run };
                }
            }
            
            return new JsonResult(result.Values.ToList());
        }

        [HttpGet("/api/projectrunsignal/{projectrun}/{signal}")]
        public ActionResult SendSignal(int projectrun, ProjectRunSignal signal)
        {
            try{
                ProjectRunControl control = new ProjectRunControl{ ProjectRunId = projectrun, Signal = signal};
                _context.ProjectRunControls.Add(control);
                _context.SaveChanges();
                return Ok();
            }
            catch(Exception ex){
                Serilog.Log.Error("Abort failed", ex);
                return NotFound();
            }
        }

        [HttpGet("/api/aborttrainig/{projectrun}")]
        public ActionResult<string> AbortTraining(int projectrun)
        {
            try{
                ProjectRunControl control = new ProjectRunControl{ ProjectRunId = projectrun, Signal = 0};
                _context.ProjectRunControls.Add(control);
                _context.SaveChanges();
                return Ok("Terminated");
            }
            catch(Exception ex){
                Serilog.Log.Error("Abort failed", ex);
                return NotFound();
            }
        }
    }
}