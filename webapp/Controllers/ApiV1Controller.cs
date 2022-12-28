using System;
using System.Runtime.CompilerServices;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.ModelBinding;
using Microsoft.EntityFrameworkCore;
using DKWebapp.Models;
using Newtonsoft.Json;
using Newtonsoft.Json.Serialization;
using System.Net.Http;
using Swashbuckle.AspNetCore.Annotations;
using DKWebapp.Models.ApiPoco;

[assembly: InternalsVisibleTo("DKWebappTest")]
namespace DKWebapp.Controllers
{
    [SwaggerTag("Create, read and update hps")]
    [Produces("application/json")]
    [Route("api/v1")]
    [ApiController]
    public class ApiV1Controller : ControllerBase
    {
        private readonly ProjectContext _context;
        public ApiV1Controller(ProjectContext context)
        {
            _context = context;
        }

        /// <summary>
        /// Get all projects
        /// </summary>
        /// <remarks>
        /// Example:&#xA;
        ///     GET /projects
        /// </remarks>
        /// <response code="200">Returns the projects</response>
        [HttpGet("projects")]
        public async Task<ActionResult<IEnumerable<ApiProject>>> GetProjects()
        {
            var projects = await _context.Projects.Include(a => a.HydroSystem).ToListAsync();
            return PocoConverter.Convert(projects);
        }

        /// <summary>
        /// Creates a project on specified hydrosystem UID and project name.
        /// </summary>
        /// <remarks>
        /// Example:&#xA;
        ///     POST /projects?name=hpsProject&amp;hydrosystemUid=00000000-0000-0000-0000-000000000000
        ///
        /// </remarks>
        /// <param name = "name">Provide a unique name for the project</param>
        /// <param name = "hydrosystemUid">Hydrosystem UID for an existing system</param>
        /// <response code="200">Returns the created project</response>
        [HttpPost("projects")]
        public async Task<ActionResult<ApiProject>> AddProject(
            [FromQuery, BindRequired]string name, 
            [FromQuery, BindRequired]string hydrosystemUid)
        {
            var error = ValidateArguments(nameof(name), name, nameof(hydrosystemUid), hydrosystemUid);
            if (error != null) return error;

            var hydroSystem = await _context.HydroSystems.Where(f => f.HydroSystemUid == hydrosystemUid).FirstOrDefaultAsync();
            if (hydroSystem == null) return NotFound(String.Format("Hydrosystem with uid '{0}' was not found.", hydrosystemUid));

            var project = await _context.Projects.Where(p => p.Name == name).FirstOrDefaultAsync();
            if (project != null) return BadRequest(String.Format("Project name '{0}' is already in use.", name));

            project = new Project
            {
                Name = name,
                ProjectUid = Guid.NewGuid().ToString("D"),
                HydroSystemId = hydroSystem.HydroSystemId
            };

            await _context.AddAsync(project);
            await _context.SaveChangesAsync();

            project = await _context.Projects.Where(p => p.ProjectUid == project.ProjectUid).Include(a => a.HydroSystem).FirstOrDefaultAsync();

            return PocoConverter.Convert(project);
        }

        /// <summary>
        /// Start a run for the given project.
        /// </summary>
        /// <remarks>
        /// Example:&#xA;
        ///     PUT /projects/00000000-0000-0000-0000-000000000000/run?forecastUid=00000000-0000-0000-0000-00000000000
        ///     body RunSettings{ ... }
        /// </remarks>
        /// <param name="projectUid">Uid of the project.</param>
        /// <param name="forecastUid">Uid of the forecast to use in the run.</param>
        /// <param name="settings">Settingsobject containing run parameters</param>
        /// <response code="200">Returns the created project run</response>
        /// <returns></returns>
        [Consumes("application/json")]
        [HttpPut("projects/{projectUid}/run")]
        public async Task<ActionResult<ApiRun>> RunProject(
            string projectUid, 
            [FromQuery, BindRequired]string forecastUid, 
            [FromBody, BindRequired] RunSettings settings)
        {
            var error = ValidateArguments(nameof(projectUid), projectUid, nameof(forecastUid), forecastUid, nameof(settings), settings);
            if (error != null) return error;

            var project = await _context.Projects.Where(p => p.ProjectUid == projectUid)
                .Include(p => p.HydroSystem).ThenInclude(h => h.Reservoirs).FirstOrDefaultAsync();
            if (project == null) return NotFound(String.Format("Project with uid '{0}' was not found.", projectUid));

            var forecast = await _context.Forecasts.Where(f => f.ForecastUid == forecastUid).FirstOrDefaultAsync();
            if (forecast == null) return NotFound(String.Format("Forecast with uid '{0}' was not found.", forecastUid));

            var reservoirs = await _context.Reservoirs.Where(r => r.HydroSystemId == project.HydroSystemId).ToListAsync();

            var settingsError = ValidateSettingsObject(settings, project, forecast);
            if (settingsError != null) return settingsError;

            var jsonSerializerSettings = new JsonSerializerSettings
            {
                ContractResolver = new DefaultContractResolver
                {
                    NamingStrategy = new CamelCaseNamingStrategy()
                }
            };

            var json = JsonConvert.SerializeObject(settings, jsonSerializerSettings);

            var previousProjectRun = await _context.ProjectRuns
                .Where(p => p.ProjectRunGuid == settings.PreviousProjectRunUid).Where(p => p.ProjectId == project.ProjectId).FirstOrDefaultAsync();
            if (previousProjectRun == null && settings.PreviousProjectRunUid != null)
            {
                return NotFound(String.Format("PreviousProjectRunUid with uid '{0}' was not found in project.", settings.PreviousProjectRunUid));
            }
            var previousQValueProjectRun = await _context.ProjectRuns
                .Where(p => p.ProjectRunGuid == settings.PreviousQValueProjectRunUid).Where(p => p.ProjectId == project.ProjectId).FirstOrDefaultAsync();
            if (previousQValueProjectRun == null && settings.PreviousQValueProjectRunUid != null)
            {
                return NotFound(String.Format("PreviousQValueProjectRunUid with uid '{0}' was not found in project.", settings.PreviousQValueProjectRunUid));
            }

            if (previousProjectRun != null)
            {
                var previousError = ValidatePreviousSettings(settings, JsonConvert.DeserializeObject<RunSettings>(previousProjectRun.ApiSettings));
                if (previousError != null) return previousError;
            }
            if (previousQValueProjectRun != null)
            {
                var previousError = ValidatePreviousSettings(settings, JsonConvert.DeserializeObject<RunSettings>(previousQValueProjectRun.ApiSettings));
                if (previousError != null) return previousError;
            }

            ProjectRun run = new ProjectRun
            {
                ProjectId = project.ProjectId,
                ApiSettings = json,
                ProjectRunGuid = Guid.NewGuid().ToString("D"),
                Comment = settings.Comment,
                ForecastId = forecast.ForecastId,
                PreviousProjectRunId = previousProjectRun == null ? (int?)null : previousProjectRun.ProjectRunId,
                PreviousQValueProjectRunId = previousQValueProjectRun == null ? (int?)null : previousQValueProjectRun.ProjectRunId
            };

            await _context.AddAsync(run);
            await _context.SaveChangesAsync();

            foreach (Reservoir res in reservoirs)
            {
                ProjectRunStartVolume startVol = new ProjectRunStartVolume
                {
                    ProjectRunId = run.ProjectRunId,
                    ReservoirId = res.ReservoirId,
                    Value = settings.StartVolumes[res.Name],
                };
                await _context.AddAsync(startVol);
            }
            await _context.SaveChangesAsync();

            using (HttpClient client = new HttpClient())
            {
                var uri = Static.PythonEndpoint + String.Format("start/{0}/{1}", projectUid, run.ProjectRunId);

                try
                {
                    HttpResponseMessage result = await client.GetAsync(uri);

                    if (!result.IsSuccessStatusCode)
                    {
                        _context.ProjectRuns.Remove(run);
                        await _context.SaveChangesAsync();
                        return StatusCode((int)result.StatusCode, "Internal problem. Please contact support.");
                    }
                }
                catch (Exception)
                {

                    _context.ProjectRuns.Remove(run);
                    await _context.SaveChangesAsync();
                    return StatusCode((int)StatusCodes.Status500InternalServerError, "There is a problem accessing the backend service. Please contact support.");
                }
            }

            return PocoConverter.Convert(run);
        }

        internal ActionResult ValidatePreviousSettings(RunSettings currentSettings, RunSettings previousSettings)
        {
            TimeSpan currentDays = calculateTimeSpan(currentSettings.StepResolution, currentSettings.StepFrequency, currentSettings.StepsInEpisode);
            TimeSpan previosDays = calculateTimeSpan(previousSettings.StepResolution, previousSettings.StepFrequency, previousSettings.StepsInEpisode);

            if (currentDays > previosDays)
            {
                string requestText = "Time period for current run cannot be longer than previous runs. ";
                requestText += $"Verify {nameof(currentSettings.StepResolution)}, {nameof(currentSettings.StepFrequency)} ";
                requestText += $"or {nameof(currentSettings.StepsInEpisode)}.";
                return BadRequest(requestText);
            }

            return null;
        }

        internal ActionResult ValidateSettingsObject(RunSettings settings, Project project, Forecast forecast)
        {
            if (project.HydroSystemId != forecast.HydroSystemId)
                return BadRequest(String.Format("Forecast with uid {} is not valid for specified project and its linked hydrosystem.", forecast.ForecastUid));

            // Assert episode length is less than or equal to the forecast length
            var series_links = _context.SeriesLinks.Where(s => s.ForecastId == forecast.ForecastId).ToArray();
            var series = _context.TimeDataSeries.Where(s => s.TimeDataSeriesId == series_links[0].PriceSeriesId).FirstOrDefault();
            var forecastStartTime = series.StartTime;
            var forecastEndTime = series.EndTime;
            var episodeTimeSpan = calculateTimeSpan(settings.StepResolution, settings.StepFrequency, settings.StepsInEpisode);
            var episodeEndTime = forecastStartTime + episodeTimeSpan;

            // if (settings.EndStateIncentive == EndStateIncentive.QValue){
            //     if (settings.PreviousQValueProjectRunUid == null){
            //         string requestText = $"{nameof(settings.PreviousQValueProjectRunUid)} has to be set when {nameof(EndStateIncentive.QValue)}";
            //         requestText +=  $"is set for {nameof(EndStateIncentive)}";
            //         return BadRequest(requestText);
            //     }
            // }

            if (episodeEndTime > forecastEndTime)
            {
                string requestText = $"End time of episode {episodeEndTime} comes after end time of forecast {forecastEndTime}. ";
                requestText += $"Consider reducing {nameof(settings.StepResolution)}, {nameof(settings.StepFrequency)} or {nameof(settings.StepsInEpisode)}";
                return BadRequest(requestText);
            }

            if (series_links.Count() < settings.EvaluationEpisodes)
            {
                return BadRequest($"The forecast contains {series_links.Count()} scenarios. Value for {nameof(settings.EvaluationEpisodes)} has to be less than or equal to that.");
            }

            if (settings.StartVolumes == null || settings.StartVolumes.Count < 1)
            {
                return BadRequest("Start volumes must be specified for all reservoirs");
            }

            var specified_res = settings.StartVolumes.Keys;
            var expected_res = from r in project.HydroSystem.Reservoirs select r.Name;

            if (specified_res.Intersect(expected_res).Count() != expected_res.Count())
                return BadRequest(String.Format("Expected volumes for reservoirs {}, but got {}",
                    String.Join(",", expected_res), String.Join(",", specified_res)));

            foreach (var res in project.HydroSystem.Reservoirs)
            {
                var vol = settings.StartVolumes[res.Name];
                if (vol > res.MaxVolume || vol < res.MinVolume)
                    return BadRequest(String.Format("Expected start volume for reservoir {} to be >= {} and <= {}, but got {}",
                    res.Name, res.MinVolume, res.MaxVolume, vol));
            }
            return null;
        }

        internal TimeSpan calculateTimeSpan(StepResolution stepResolution, int freq, int steps)
        {
            switch (stepResolution)
            {
                case StepResolution.Day:
                    return new TimeSpan(freq * steps, 0, 0, 0);

                case StepResolution.Week:
                    return new TimeSpan(freq * 7 * steps, 0, 0, 0);

                case StepResolution.Hour:
                    return new TimeSpan(freq * steps, 0, 0);
                default:
                    throw new ArgumentException("Unhandled value: " + stepResolution.ToString());
            }
        }

        /// <summary>
        /// Evaluate a project run given runsettings and forecast
        /// </summary>
        /// <remarks>
        /// Example:&#xA;
        /// &#009;POST /projectruns/00000000-0000-0000-0000-000000000000/evaluate?forecastUid=00000000-0000-0000-0000-000000000000
        ///     body RunSettings{ ... }
        ///
        /// </remarks>
        /// <param name = "projectRunUid">Project run UID for an existing project run</param>
        /// <param name = "forecastUid">Forecast UID for an existing forecast</param>
        /// <param name = "settings">Runsettings</param>
        /// <response code="200">Returns evaluation for the specified project run</response>
        [Consumes("application/json")]
        [HttpPut("projectruns/{projectRunUid}/evaluate")]
        public async Task<ActionResult<ApiRun>> EvaluateProject(
            string projectRunUid, 
            [FromQuery, BindRequired]string forecastUid, 
            [FromBody, BindRequired] RunSettings settings)
        {
            var error = ValidateArguments(nameof(projectRunUid), projectRunUid, nameof(forecastUid), forecastUid, nameof(settings), settings);
            if (error != null) return error;

            var projectRun = await _context.ProjectRuns.Where(p => p.ProjectRunGuid == projectRunUid)
                .Include(p => p.Project).ThenInclude(p => p.HydroSystem).ThenInclude(h => h.Reservoirs).FirstOrDefaultAsync();

            if (projectRun == null) return NotFound(String.Format("ProjectRun with uid '{0}' was not found.", projectRunUid));
            var project = projectRun.Project;

            var forecast = await _context.Forecasts.Where(f => f.ForecastUid == forecastUid).Include(f => f.HydroSystem).FirstOrDefaultAsync();
            if (forecast == null) return NotFound(String.Format("Forecast with uid '{0}' was not found.", forecastUid));

            var settingsError = ValidateSettingsObject(settings, project, forecast);
            if (settingsError != null) return settingsError;

            var init_vols = new List<ProjectRunStartVolume>();
            foreach (var res in project.HydroSystem.Reservoirs)
            {
                var vol = settings.StartVolumes[res.Name];
                init_vols.Add(new ProjectRunStartVolume() { ReservoirId = res.ReservoirId, Value = vol });
            }

            var agent_to_use = await GetBestAgent(projectRunUid);

            var jsonSerializerSettings = new JsonSerializerSettings
            {
                ContractResolver = new DefaultContractResolver
                {
                    NamingStrategy = new CamelCaseNamingStrategy()
                }
            };

            var json = JsonConvert.SerializeObject(settings, jsonSerializerSettings);

            ProjectRun run = new ProjectRun
            {
                ProjectId = project.ProjectId,
                ApiSettings = json,
                ProjectRunGuid = Guid.NewGuid().ToString("D"),
                Comment = settings.Comment,
                ForecastId = forecast.ForecastId,
                EvaluatedOn = agent_to_use.AgentId
            };

            await _context.AddAsync(run);
            await _context.SaveChangesAsync();

            init_vols.ForEach(v => v.ProjectRunId = run.ProjectRunId);
            init_vols.ForEach(v => _context.Add(v));

            await _context.SaveChangesAsync();

            using (HttpClient client = new HttpClient())
            {
                var uri = Static.PythonEndpoint + String.Format("evaluate/{0}", run.ProjectRunGuid);

                try
                {
                    HttpResponseMessage result = await client.GetAsync(uri);

                    if (!result.IsSuccessStatusCode)
                    {
                        _context.ProjectRuns.Remove(run);
                        await _context.SaveChangesAsync();
                        return StatusCode((int)result.StatusCode, "Internal problem. Please contact support.");
                    }
                }
                catch (Exception)
                {

                    _context.ProjectRuns.Remove(run);
                    await _context.SaveChangesAsync();
                    return StatusCode((int)StatusCodes.Status500InternalServerError, "There is a problem accessing the backend service. Please contact support.");
                }
            }

            return PocoConverter.Convert(run);
        }        
        
        /// <summary>
        /// Get all project runs for a specified project
        /// </summary>
        /// <remarks>
        /// Example:&#xA;
        /// &#009;GET /projects/00000000-0000-0000-0000-000000000000/projectruns/
        ///
        /// </remarks>
        /// <param name = "projectUid">Project UID for an existing project</param>
        /// <response code="200">Returns all project runs for the specified project</response>
        [HttpGet("projects/{projectUid}/projectruns")]
        public async Task<ActionResult<IEnumerable<ApiRun>>> GetProjectRuns(string projectUid)
        {
            return await GetRuns(projectUid, (evaluatedOn) => evaluatedOn == null);
        }

        /// <summary>
        /// Get all evaluations for a specified project
        /// </summary>
        /// <remarks>
        /// Example:&#xA;
        /// &#009;GET /projects/00000000-0000-0000-0000-000000000000/evaluations/
        ///
        /// </remarks>
        /// <param name = "projectUid">Project UID for an existing project</param>
        /// <response code="200">Returns all project runs for the specified project</response>
        [HttpGet("projects/{projectUid}/evaluations")]
        public async Task<ActionResult<IEnumerable<ApiRun>>> GetEvaluations(string projectUid)
        {
            return await GetRuns(projectUid, (evaluatedOn) => evaluatedOn != null);
        }

        private async Task<ActionResult<IEnumerable<ApiRun>>> 
        GetRuns(string projectUid, Func<int?, bool> filter)
        {
            var error = ValidateArguments(nameof(projectUid), projectUid);
            if (error != null) return error;

            var project = await _context.Projects.Where(p => p.ProjectUid == projectUid).FirstOrDefaultAsync();
            if (project == null) return NotFound(String.Format("Project with uid '{0}' was not found.", projectUid));

            var result = await _context.ProjectRuns.Where(r => r.ProjectId == project.ProjectId && filter(r.EvaluatedOn)).Include(r => r.Forecast).ToListAsync();
            return PocoConverter.Convert(result);
        }

        /// <summary>
        /// Returns a template for run settings for the specified project Uid.&#xA;
        /// </summary>
        /// <remarks>
        /// Example:&#xA;
        /// &#009;GET /projects/00000000-0000-0000-0000-000000000000/runsettingstemplate
        ///
        /// </remarks>
        /// <param name = "projectUid">Project UID for an existing project</param>
        /// <response code="200">Returns all project runs for the specified project</response>
        [HttpGet("projects/{projectUid}/runsettingstemplate")]
        public async Task<ActionResult<RunSettings>> GetProjectRunSettingsTemplate(string projectUid)
        {
            var error = ValidateArguments(nameof(projectUid), projectUid);
            if (error != null) return error;

            var project = await _context.Projects.Where(p => p.ProjectUid == projectUid).FirstOrDefaultAsync();
            if (project == null) return NotFound(String.Format("Project with uid '{0}' was not found.", projectUid));

            var queryResult = await (
                from hydros in _context.HydroSystems
                join res in _context.Reservoirs
                on hydros.HydroSystemId equals res.HydroSystemId
                where hydros.HydroSystemId == project.HydroSystemId
                select res
            ).ToListAsync();
            if (queryResult.Count == 0) return NotFound(String.Format("No hydrosystem found for project with uid '{0}'", projectUid));

            Dictionary<string, double> resStartVolumes = new Dictionary<string, double>();
            foreach (Reservoir res in queryResult)
            {
                resStartVolumes.Add(res.Name, res.MinVolume);
            }

            RunSettings settings = new RunSettings
            {
                StartVolumes = resStartVolumes,
                StepsInEpisode = 104,
                StepFrequency = 1,
                StepResolution = StepResolution.Week,
                RewardScaleFactor = 10,
                PriceOfSpillage = 1,
                ForecastClusters = 7,
                RandomizeStartVolume = true,
                DiscountRate = 0.04,
                TrainEpisodes = 10000,
                EvaluationEpisodes = 5,
                EvaluationInterval = 30,
                EndStateIncentive = EndStateIncentive.MeanEnergyPrice,
                Noise = Noise.Off
            };
            return settings;
        }

        /// <summary>
        /// Get all hydrosystems
        /// </summary>
        /// <remarks>
        /// Example:&#xA;
        ///     GET /hydrosystems
        /// </remarks>
        /// <response code="200">Returns all hydrosystems</response>
        [HttpGet("hydrosystems")]
        public async Task<ActionResult<IEnumerable<ApiHydroSystem>>> GetHydroSytems()
        {
            var hydrosystems = await _context.HydroSystems.ToListAsync();
            return PocoConverter.Convert(hydrosystems);
        }

        /// <summary>
        /// Get all reservoirs for specified hydrosystem
        /// </summary>
        /// <remarks>
        /// Remark:&#xA;
        /// Hydrosystem UID must exist&#xD;
        ///
        ///
        /// Example:&#xA;
        ///     GET /hydrosystems/00000000-0000-0000-0000-000000000000/reservoirs
        /// </remarks>
        /// <response code="200">Returns all reservoirs for specified hydrosystem</response>
        [HttpGet("hydrosystems/{hydrosystemUid}/reservoirs")]
        public async Task<ActionResult<IEnumerable<ApiReservoir>>> GetReservoirs(string hydrosystemUid)
        {
            var error = ValidateArguments(nameof(hydrosystemUid), hydrosystemUid);
            if (error != null) return error;

            var queryResult = await (
                from hydros in _context.HydroSystems
                where hydros.HydroSystemUid == hydrosystemUid
                select hydros
            ).Include(h => h.Reservoirs).FirstOrDefaultAsync();

            if (queryResult == null) return NotFound(String.Format("No reservoirs for hydrosystem with uid '{0}' were found", hydrosystemUid));
            return PocoConverter.Convert(queryResult.Reservoirs);
        }


        [HttpGet("hydrosystems/{hydrosystemUid}")]
        private async Task<ActionResult<String>> GetHydroSystemMetadata(string hydrosystemUid)
        {

            var error = ValidateArguments(nameof(hydrosystemUid), hydrosystemUid);
            if (error != null) return error;

            var hydroSystem = await _context.HydroSystems.Where(h => h.HydroSystemUid == hydrosystemUid).FirstOrDefaultAsync();
            if (hydroSystem == null) return NotFound(String.Format("Hydrosystem with uid '{0}' was not found", hydrosystemUid));
            string hydroSystemJson = null;
            using (HttpClient client = new HttpClient())
            {
                var uri = Static.PythonEndpoint + String.Format("/hydropowersystem/{0}", hydroSystem.Name.ToLowerInvariant());
                try
                {
                    HttpResponseMessage result = await client.GetAsync(uri);
                    hydroSystemJson = await result.Content.ReadAsStringAsync();
                    if (!result.IsSuccessStatusCode)
                    {
                        return StatusCode((int)result.StatusCode, "Internal problem. Please contact support.");
                    }
                }
                catch (Exception)
                {
                    return StatusCode((int)StatusCodes.Status500InternalServerError, "There is a problem accessing the backend service. Please contact support.");
                }
            }
            return null; //hydroSystemJson;
        }

        /// <summary>
        /// Get list of all forecasts for specified hydrosystem
        /// </summary>
        /// <remarks>
        /// Remark:&#xA;
        /// Hydrosystem UID must exist&#xD;
        ///
        ///
        /// Example:&#xA;
        ///     GET /hydrosystems/00000000-0000-0000-0000-000000000000/forecasts
        /// </remarks>
        /// <response code="200">Returns all reservoirs for specified hydrosystem</response>
        [HttpGet("hydrosystems/{hydrosystemUid}/forecasts")]
        public async Task<ActionResult<IEnumerable<ApiForecast>>> GetForecasts(string hydrosystemUid)
        {
            var error = ValidateArguments(nameof(hydrosystemUid), hydrosystemUid);
            if (error != null) return error;

            var forecasts = await (from f in _context.Forecasts
                                   join h in _context.HydroSystems on f.HydroSystemId equals h.HydroSystemId
                                   where h.HydroSystemUid == hydrosystemUid
                                   select f).ToListAsync();

            return PocoConverter.Convert(forecasts);
        }

        /// <summary>
        /// Create a forecast for a given hydrosystem
        /// </summary>
        /// <remarks>
        /// Example:&#xA;
        ///     POST /forecasts?hydrosystemUid=00000000-0000-0000-0000-000000000000&amp;forecastName=hpsForecast
        /// </remarks>
        /// <param name="hydrosystemUid">Uid of the hydrosystem.</param>
        /// <param name="forecastName">Name of the forecast to be created</param>
        /// <response code="200">Returns the created project run</response>
        /// <returns></returns>
        [HttpPost("forecasts")]
        public async Task<ActionResult<ApiForecast>> PostForecast(
            [FromQuery, BindRequired]string hydrosystemUid,
            [FromQuery, BindRequired]string forecastName
        )
        {
            var error = ValidateArguments(nameof(hydrosystemUid), hydrosystemUid, nameof(forecastName), forecastName);
            if (error != null) return error;
            var hydroSystem = await _context.HydroSystems.Where(h => h.HydroSystemUid == hydrosystemUid).FirstOrDefaultAsync();
            if (hydroSystem == null) return NotFound(String.Format("HydroSsytem with uid '{}' was not found", hydrosystemUid));

            var forecast = await _context.Forecasts.Where(f => f.Name == forecastName && f.HydroSystemId == hydroSystem.HydroSystemId).FirstOrDefaultAsync();
            if (forecast != null) return BadRequest(String.Format("Forecast for hydrosystem '{}' with name '{}' already exists.", hydroSystem.Name, forecastName));

            Upload newUpload = new Upload { UploadTime = DateTimeOffset.UtcNow, SourceFile = hydroSystem.Name + " " + forecastName };
            await _context.AddAsync(newUpload);
            await _context.SaveChangesAsync();

            forecast = new Forecast
            {
                ForecastUid = Guid.NewGuid().ToString("D"),
                UploadId = newUpload.UploadId,
                HydroSystemId = hydroSystem.HydroSystemId,
                Name = forecastName
            };
            await _context.AddAsync(forecast);
            await _context.SaveChangesAsync();

            return PocoConverter.Convert(forecast);
        }

        /// <summary>
        /// Post scenario data for specified scenario and forecast
        /// </summary>
        /// <remarks>
        /// Remarks:&#xA;
        /// Scenarios for a given forecast must be of equal length (timesteps).<br/>
        ///
        /// Example:&#xA;
        ///     POST /forecasts/00000000-0000-0000-0000-000000000000?scenario=2021
        ///     body ApiForecastScenario { ... }
        /// </remarks>
        /// <response code="200">OK</response>
        [HttpPost("forecasts/{forecastUid}")]
        [Consumes("application/json")]
        public async Task<ActionResult> PostForecastScenario(
            string forecastUid,
            [FromQuery, BindRequired]string scenario,
            [FromBody, BindRequired] ApiForecastScenario forecastScenario
        )
        {
            var error = ValidateArguments(nameof(forecastUid), forecastUid, nameof(scenario), scenario);
            if (error != null) return error;

            var forecast = await _context.Forecasts.Where(f => f.ForecastUid == forecastUid).FirstOrDefaultAsync();
            if (forecast == null) return NotFound(String.Format("Forecast with uid '{0}' was not found", forecastUid));

            if (forecastScenario.InflowSeries.Count != forecastScenario.PriceSeries.Count || forecastScenario.InflowSeries.Count != forecastScenario.TimeIndex.Count)
            {
                return BadRequest("The length of InflowSeries, PriceSeries, and TimeSeries are not equal");
            }
            using (var transaction = _context.Database.BeginTransaction())
            {
                //Check if scenario has already been uploaded
                var existingScenarios = await _context.TimeDataSeries.Where(tds => tds.UploadId == forecast.UploadId).Select(tds => tds.Description).ToListAsync();
                if (existingScenarios.Contains(scenario))
                {
                    return BadRequest(String.Format("Scenario '{0}' already exists for forecast '{1}'", scenario, forecastUid));
                }

                var previousSeries = await _context.TimeDataSeries.Where(tds => tds.UploadId == forecast.UploadId).Include(val => val.Values).FirstOrDefaultAsync();
                if(previousSeries != null)
                {
                    // If there is a previous series, compare length, If not proceed with creating series
                    List<DateTimeOffset> previousTimeIndex = previousSeries.Values.Select(t => t.TimeStampOffset).ToList();
                    if (!Enumerable.SequenceEqual(previousTimeIndex, forecastScenario.TimeIndex))
                    {
                        return BadRequest(String.Format("Timeindex varies from previously uploaded scenario for forecastUid '{0}'", forecast.ForecastUid));
                    }
                }


                TimeDataSeries inflowSeries = new TimeDataSeries
                {
                    UploadId = forecast.UploadId,
                    StartTime = forecastScenario.TimeIndex.First(),
                    EndTime = forecastScenario.TimeIndex.Last(),
                    Description = scenario,
                    Type = TimeDataSeriesType.Inflow
                };
                await _context.AddAsync(inflowSeries);

                TimeDataSeries priceSeries = new TimeDataSeries
                {
                    UploadId = forecast.UploadId,
                    StartTime = forecastScenario.TimeIndex.First(),
                    EndTime = forecastScenario.TimeIndex.Last(),
                    Description = scenario,
                    Type = TimeDataSeriesType.Price
                };
                await _context.AddAsync(priceSeries);
                await _context.SaveChangesAsync();
                for (int i = 0; i < forecastScenario.TimeIndex.Count; i++)
                {
                    TimeDataValue inflowData = new TimeDataValue
                    {
                        TimeDataSeriesId = inflowSeries.TimeDataSeriesId,
                        TimeStampOffset = forecastScenario.TimeIndex[i],
                        Value = forecastScenario.InflowSeries[i]
                    };
                    TimeDataValue priceData = new TimeDataValue
                    {
                        TimeDataSeriesId = priceSeries.TimeDataSeriesId,
                        TimeStampOffset = forecastScenario.TimeIndex[i],
                        Value = forecastScenario.PriceSeries[i]
                    };
                    await _context.AddAsync(inflowData);
                    await _context.AddAsync(priceData);
                }
                await _context.SaveChangesAsync();
                TimeDataSeriesLink seriesLink = new TimeDataSeriesLink
                {
                    UploadId = forecast.UploadId,
                    ForecastId = forecast.ForecastId,
                    InflowSeriesId = inflowSeries.TimeDataSeriesId,
                    PriceSeriesId = priceSeries.TimeDataSeriesId
                };
                await _context.AddAsync(seriesLink);

                await _context.SaveChangesAsync();
                transaction.Commit();
            }


            return Ok();
        }


        /// <summary>
        /// Get All scenarios for specified forecast and hydrosystem
        /// </summary>
        /// <remarks>
        /// Example:&#xA;
        ///     GET /forecasts/00000000-0000-0000-0000-000000000000
        /// </remarks>
        /// <response code="200">Returns list of forecasts</response>
        [HttpGet("forecasts/{forecastUid}")]
        public async Task<ActionResult<ApiForecastScenarios>> GetForecastScenarios(string forecastUid)
        {
            var error = ValidateArguments(nameof(forecastUid), forecastUid);
            if (error != null) return error;

            var forecast = await _context.Forecasts.Where(f => f.ForecastUid == forecastUid).FirstOrDefaultAsync();
            if(forecast == null) return NotFound(String.Format("Forecast with uid '{}' waas not found", forecastUid));

            var result = await (
                from forc in _context.Forecasts
                join link in _context.SeriesLinks
                on forc.ForecastId equals link.ForecastId
                join tds in _context.TimeDataSeries
                on link.InflowSeriesId equals tds.TimeDataSeriesId
                where forc.ForecastId == forecast.ForecastId
                select tds.Description
            ).ToListAsync();

            ApiForecastScenarios forecastScenarios = new ApiForecastScenarios
            {
                Scenarios = result
            };

            return forecastScenarios;
        }

        /// <summary>
        /// Get scenario data for specified scenario and forecast
        /// </summary>
        /// <remarks>
        /// Example:&#xA;
        ///     GET /forecasts/00000000-0000-0000-0000-000000000000/scenarios/2017
        /// </remarks>
        /// <response code="200">Returns scenario data</response>
        [HttpGet("forecasts/{forecastUid}/scenarios/{scenario}")]
        public async Task<ActionResult<ApiForecastScenario>> GetForecastScenario(string forecastUid, string scenario)
        {
            var error = ValidateArguments(nameof(forecastUid), forecastUid, nameof(scenario), scenario);
            if (error != null) return error;

            var forecast = await _context.Forecasts.Where(f => f.ForecastUid == forecastUid).FirstOrDefaultAsync();
            if (forecast == null) return NotFound(String.Format("Forecast with uid '{0}' was not found.", forecastUid));

            var result = await ( 
                from link in _context.SeriesLinks
                join tds in _context.TimeDataSeries
                on link.InflowSeriesId equals tds.TimeDataSeriesId
                where link.ForecastId == forecast.ForecastId && tds.Description == scenario
                select link
            ).FirstOrDefaultAsync();
            if (result == null) return NotFound(String.Format("Scenario '{0}' not found for forecast with uid '{1}'.", scenario, forecastUid));

            var timeDataValues = await _context.TimeDataValue.Where(
                tdv => tdv.TimeDataSeriesId == result.InflowSeriesId || tdv.TimeDataSeriesId == result.PriceSeriesId).ToListAsync();

            ApiForecastScenario forecastScenario = new ApiForecastScenario
            {
                TimeIndex = timeDataValues.Where(tdv => tdv.TimeDataSeriesId == result.InflowSeriesId).Select(tdv => tdv.TimeStampOffset).ToList(),
                InflowSeries = timeDataValues.Where(tdv => tdv.TimeDataSeriesId == result.InflowSeriesId).Select(tdv => tdv.Value).ToList(),
                PriceSeries = timeDataValues.Where(tdv => tdv.TimeDataSeriesId == result.PriceSeriesId).Select(tdv => tdv.Value).ToList()
            };

            return forecastScenario;
        }

        /// <summary>
        /// Get run details for specified project run
        /// </summary>
        /// <remarks>
        /// Example:&#xA;
        ///     GET /projectruns/00000000-0000-0000-0000-000000000000/rundetails
        /// </remarks>
        /// <response code="200">Returns detail for project run</response>
        [HttpGet("projectruns/{projectRunUid}/rundetails")]
        public async Task<ActionResult<RunDetails>> GetRunDetails(string projectRunUid)
        {
            var error = ValidateArguments(nameof(projectRunUid), projectRunUid);
            if (error != null) return error;

            var result = await
                (from prjrun in _context.ProjectRuns
                 join agent in _context.Agents
                 on prjrun.ProjectRunId equals agent.ProjectRunId
                 join series in _context.TrainStepData
                 on agent.AgentId equals series.AgentId
                 where series.Type == "scalars" && prjrun.ProjectRunGuid == projectRunUid
                 select series).Include(s => s.Values).ToListAsync();

            return PocoConverter.Convert(result);
        }


        /// <summary>
        /// Get current progress for project run
        /// </summary>
        /// <remarks>
        /// Example:&#xA;
        ///     GET /projectruns/00000000-0000-0000-0000-000000000000/progress
        /// </remarks>
        /// <response code="200">Returns progress for project run</response>
        [HttpGet("projectruns/{projectRunUid}/progress")]
        public async Task<ActionResult<RunDetails>> GetProgress(string projectRunUid)
        {
            var error = ValidateArguments(nameof(projectRunUid), projectRunUid);
            if (error != null) return error;

            var result = await
                (from prjrun in _context.ProjectRuns
                 join agent in _context.Agents
                 on prjrun.ProjectRunId equals agent.ProjectRunId
                 join series in _context.TrainStepData
                 on agent.AgentId equals series.AgentId
                 join value in _context.TrainStepValues
                 on series.StepSeriesId equals value.StepSeriesId
                 where series.Type == "scalars" && series.Description == "Best Return" && prjrun.ProjectRunGuid == projectRunUid
                 group value by value.Step into g
                 select new { Step = g.Key, Value = g.Max(v => v.Value), Count = g.Count() }
                 ).ToListAsync();

            RunDetails details = new RunDetails() { Progress = 100.0, Status = new List<ApiStepSeries>() };

            var stepseries = new ApiStepSeries() { Steps = new List<double>(), Values = new List<double>() };
            foreach (var v in result)
            {
                stepseries.Steps.Add(v.Step);
                stepseries.Values.Add(v.Value);
            }
            details.Status.Add(stepseries);
            return details;
        }

        private async Task<Agent> GetBestAgent(string projectRunUid)
        {
            var result = await
            (
                from prjrun in _context.ProjectRuns
                join agent in _context.Agents
                on prjrun.ProjectRunId equals agent.ProjectRunId
                where prjrun.ProjectRunGuid == projectRunUid
                orderby agent.BestStepValue descending
                select agent
            ).FirstOrDefaultAsync();

            return result;
        }

        /// <summary>
        /// Get the best solution for a project run
        /// </summary>
        /// <remarks>
        /// Example:&#xA;
        ///     GET /projectruns/00000000-0000-0000-0000-000000000000/solution
        /// </remarks>
        /// <response code="200">Returns solution for project run</response>
        [HttpGet("projectruns/{projectRunUid}/solution")]
        public async Task<ActionResult<ApiReportData>> GetBestSolution(string projectRunUid)
        {
            var error = ValidateArguments(nameof(projectRunUid), projectRunUid);
            if (error != null) return error;

            var bestAgent = await GetBestAgent(projectRunUid);

            var bestAgentId = bestAgent.AgentId;
            var bestStep = bestAgent.BestStep;

            var data = (from val in _context.ReportValues
                        join ser in _context.ReportData
                        on val.ReportSeriesId equals ser.ReportSeriesId
                        join eval in _context.EvaluationEpisodes
                        on ser.EvaluationEpisodeId equals eval.EvaluationEpisodeId
                        join run in _context.ProjectRuns
                        on eval.ProjectRunId equals run.ProjectRunId
                        where val.Step == bestStep && eval.AgentId == bestAgentId && run.ProjectRunGuid == projectRunUid
                        select val
                    ).Include(val => val.ReportSeries).ThenInclude(ser => ser.EvaluationEpisode).ToList();
            return PocoConverter.Convert(data);
        }

        /// <summary>
        /// Get evaluation data for specified evaluation
        /// </summary>
        /// <remarks>
        /// Example:&#xA;
        ///     GET /evaluations/00000000-0000-0000-0000-000000000000
        /// </remarks>
        /// <response code="200">Returns an evaluation</response>
        [HttpGet("evaluations/{evaluationUid}")]
        public ActionResult<ApiReportData> GetEvaluationResult(string evaluationUid)
        {
            var error = ValidateArguments(nameof(evaluationUid), evaluationUid);
            if (error != null) return error;

            var projectRun = (from p in _context.ProjectRuns
                              where p.ProjectRunGuid == evaluationUid
                              select p).First();

            var data = (from val in _context.ReportValues
                        join ser in _context.ReportData
                        on val.ReportSeriesId equals ser.ReportSeriesId
                        join eval in _context.EvaluationEpisodes
                        on ser.EvaluationEpisodeId equals eval.EvaluationEpisodeId
                        join run in _context.ProjectRuns
                        on eval.ProjectRunId equals run.ProjectRunId
                        join agent in _context.Agents
                        on run.EvaluatedOn equals agent.AgentId
                        where run.ProjectRunId == projectRun.ProjectRunId && val.Step == 1 && agent.AgentId == projectRun.EvaluatedOn
                        select val
                    ).Include(val => val.ReportSeries).ThenInclude(ser => ser.EvaluationEpisode).ToList();

            return PocoConverter.Convert(data);
        }

        /// <summary>
        /// Attempt to terminate a running project run
        /// </summary>
        /// <remarks>
        /// Example:&#xA;
        ///     PUT /projectrun/00000000-0000-0000-0000-000000000000/terminate
        /// </remarks>
        /// <response code="200">Ok</response>
        [HttpPut("projectruns/{projectRunUid}/terminate")]
        public async Task<ActionResult<RunDetails>> Terminate(string projectRunUid)
        {
            var error = ValidateArguments(nameof(projectRunUid), projectRunUid);
            if (error != null) return error;

            var run = await _context.ProjectRuns.Where(p => p.ProjectRunGuid == projectRunUid).FirstOrDefaultAsync();
            if (run == null) return NotFound(String.Format("Projectrun with uid '{0}' was not found.", projectRunUid));

            ProjectRunControl control = new ProjectRunControl { ProjectRunId = run.ProjectRunId, Signal = ProjectRunSignal.Terminate };
            _context.ProjectRunControls.Add(control);
            _context.SaveChanges();
            return Ok();
        }

        private ActionResult ValidateArguments(params object[] data)
        {
            for (int i = 0; i < data.Length; i += 2)
            {
                var a = ValidateArgument((string)data[i], data[i + 1]);
                if (a != null) return a;
            }
            return null;
        }

        private ActionResult ValidateArgument(string name, object argument)
        {
            if ((argument is string && String.IsNullOrWhiteSpace((string)argument)) || argument == null)
                return BadRequest(String.Format("Argument {0} cannot be null or empty", name));
            return null;
        }
    }
}
