using Microsoft.EntityFrameworkCore;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using DKWebapp.Models;

namespace DKWebapp.Models
{
    public class ProjectContext : DbContext
    {
        public ProjectContext() : base()
        {

        }

        public ProjectContext(DbContextOptions options) : base(options)
        {

        }

        protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        {
            optionsBuilder.UseSqlite(Static.DBConnection);
        }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
           
            modelBuilder.Entity<StepValue>()
                .HasKey(t => new { t.StepSeriesId, t.Step });

            modelBuilder.Entity<ReportValue>()
                .HasKey(t => new { t.ReportSeriesId, t.Step, t.Index });

            modelBuilder.Entity<TimeDataValue>()
                .HasKey(t => new { t.TimeDataSeriesId, t.TimeStampOffset });

            modelBuilder.Entity<Project>()
                .HasIndex(t => t.Name).IsUnique();

            modelBuilder.Entity<ProjectRun>().HasOne(p => p.Agent).WithMany();

            modelBuilder.Entity<ProjectRun>()
                .HasOne(p => p.PreviousProjectRun).WithMany().HasForeignKey("PreviousProjectRunId");

            modelBuilder.Entity<ProjectRun>()
                .HasOne(p => p.PreviousQValueProjectRun).WithMany().HasForeignKey("PreviousQValueProjectRunId");
        }

        public DbSet<Project> Projects { get; set; }
        public DbSet<ProjectRun> ProjectRuns { get; set; }
        public DbSet<ProjectRunControl> ProjectRunControls { get; set; }
        public DbSet<Agent> Agents { get; set; }
        public DbSet<AgentControl> AgentControls { get; set; }
        public DbSet<StepSeries> TrainStepData{ get; set;}
        public DbSet<ReportSeries> ReportData{ get; set;}
        public DbSet<StepValue> TrainStepValues{ get; set;}
        public DbSet<ReportValue> ReportValues{ get; set;}
        public DbSet<Upload> Uploads { get; set; }
        public DbSet<Forecast> Forecasts { get; set; }
        public DbSet<TimeDataSeriesLink> SeriesLinks { get; set; }
        public DbSet<TimeDataSeries> TimeDataSeries { get; set; } 
        public DbSet<TimeDataValue> TimeDataValue{ get; set;}  
        public DbSet<EvaluationEpisode> EvaluationEpisodes {get; set; }
        public DbSet<HydroSystem> HydroSystems { get; set; }
        public DbSet<ProjectRunStartVolume> ProjectRunStartVolume {get; set;}
        public DbSet<Reservoir> Reservoirs { get; set; }
    }
}
