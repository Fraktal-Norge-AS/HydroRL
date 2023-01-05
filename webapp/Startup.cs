using System;
using System.Reflection;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.HttpsPolicy;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.OpenApi.Models;
using Serilog;
using Serilog.Events;
using Serilog.Sinks.SQLite;
using Serilog.AspNetCore;
using AspNetCore.Proxy;
using DKWebapp.Models;

namespace DKWebapp
{
    public class Startup
    {
        public Startup(IConfiguration configuration)
        {
            Configuration = configuration;
        }

        public IConfiguration Configuration { get; }

        // This method gets called by the runtime. Use this method to add services to the container.
        public void ConfigureServices(IServiceCollection services)
        {
            services.Configure<CookiePolicyOptions>(options =>
            {
                // This lambda determines whether user consent for non-essential cookies is needed for a given request.
                options.CheckConsentNeeded = context => true;
                options.MinimumSameSitePolicy = SameSiteMode.None;
            });

            services.AddDbContext<ProjectContext>(options => options.UseSqlite(Configuration.GetConnectionString("DKConnection")));
            services.AddMvc().SetCompatibilityVersion(CompatibilityVersion.Version_2_2)
                .AddJsonOptions(options =>
                {
                    options.SerializerSettings.Converters.Add(new Newtonsoft.Json.Converters.StringEnumConverter());
                    options.SerializerSettings.NullValueHandling = Newtonsoft.Json.NullValueHandling.Include;
                    options.SerializerSettings.MissingMemberHandling = Newtonsoft.Json.MissingMemberHandling.Error;
                });
            services.AddSwaggerGen(c =>
            {
                c.SwaggerDoc("v1", new OpenApiInfo
                {
                    Title="HydroRL API",
                    Version="v1",
                    Description="The API for HydroRL.",
                    Contact=new OpenApiContact
                    {
                        Name = "",
                        Email = "",
                    }
                });

                var xmlFile = $"{Assembly.GetExecutingAssembly().GetName().Name}.xml";
                var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
                c.OrderActionsBy((apiDesc) => $"{apiDesc.ActionDescriptor.RouteValues["controller"]}_{apiDesc.RelativePath}");
                c.IncludeXmlComments(xmlPath);
                c.EnableAnnotations();
            });
            services.AddSwaggerGenNewtonsoftSupport();
            
            services.AddProxies();
            Static.PythonEndpoint = Configuration["PythonEndpoint"];
            Static.DBConnection = Configuration.GetConnectionString("DKConnection");

            string logDb = Configuration.GetConnectionString("DKLogConnection");            

            Log.Logger = new LoggerConfiguration()
                .WriteTo.SQLite(logDb, "Logs", LogEventLevel.Information, null, true, TimeSpan.FromDays(1200), null, null, 10, 10)
                .WriteTo.Console(LogEventLevel.Information)
                .MinimumLevel.Debug()
                .CreateLogger();
            
            Log.Information("Application has been configured. Logging started");
        }

        // This method gets called by the runtime. Use this method to configure the HTTP request pipeline.
        public void Configure(IApplicationBuilder app, IHostingEnvironment env)
        {
            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
            }
            else
            {
                app.UseExceptionHandler("/Error");
                // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
                app.UseHsts();
            }

            using (var serviceScope = app.ApplicationServices.GetService<IServiceScopeFactory>().CreateScope())
            {
                var context = serviceScope.ServiceProvider.GetRequiredService<ProjectContext>();
                context.Database.Migrate();
            }

            app.UseProxies(
                proxies =>{
                    proxies.Map("api/start_agents/{uid}/{run_id}", proxy => proxy.UseHttp((_, args) => new ValueTask<string>(Static.PythonEndpoint + $"start/{args["uid"]}/{args["run_id"]}")));
                    proxies.Map("api/evaluate/{eval_id}", proxy => proxy.UseHttp((_, args) => new ValueTask<string>(Static.PythonEndpoint + $"evaluate/{args["eval_id"]}")));
                    proxies.Map("api/drawing/{system}", proxy => proxy.UseHttp((_, args) => new ValueTask<string>(Static.PythonEndpoint + $"drawing/{args["system"]}")));
                    proxies.Map("api/price/{year}/{intervals}", proxy => proxy.UseHttp((_, args) => new ValueTask<string>(Static.PythonEndpoint + $"price/{args["year"]}/{args["intervals"]}")));
                    proxies.Map("api/inflow/{year}/{intervals}", proxy => proxy.UseHttp((_, args) => new ValueTask<string>(Static.PythonEndpoint + $"inflow/{args["year"]}/{args["intervals"]}")));
                    proxies.Map("api/projectFileUpload/{filetype}", proxy => proxy.UseHttp((_, args) => new ValueTask<string>(Static.PythonEndpoint + $"postcsv/{args["filetype"]}")));
                    proxies.Map("api/create_run_settings/{uid}", proxy => proxy.UseHttp((_, args) => new ValueTask<string>(Static.PythonEndpoint + $"create_run_settings/{args["uid"]}")));
                    proxies.Map("api/create_run_settings/{uid}/{agent_id}", proxy => proxy.UseHttp((_, args) => new ValueTask<string>(Static.PythonEndpoint + $"create_run_settings/{args["uid"]}/{args["agent_id"]}")));
                });

            app.UseHttpsRedirection();
            app.UseStaticFiles();
            app.UseCookiePolicy();

            app.UseSwagger();

            app.UseSwaggerUI(c =>
            {
                 c.SwaggerEndpoint("/swagger/v1/swagger.json", "HPS API V1");
            });
            

            app.UseMvc();
        }
    }
}
