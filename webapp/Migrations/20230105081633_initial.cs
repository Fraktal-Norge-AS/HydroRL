using System;
using Microsoft.EntityFrameworkCore.Migrations;

namespace DKWebapp.Migrations
{
    public partial class initial : Migration
    {
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "HydroSystems",
                columns: table => new
                {
                    HydroSystemId = table.Column<int>(nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    HydroSystemUid = table.Column<string>(nullable: true),
                    Name = table.Column<string>(nullable: true),
                    Description = table.Column<string>(nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_HydroSystems", x => x.HydroSystemId);
                });

            migrationBuilder.CreateTable(
                name: "Uploads",
                columns: table => new
                {
                    UploadId = table.Column<int>(nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    UploadTime = table.Column<DateTimeOffset>(nullable: false),
                    SourceFile = table.Column<string>(nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Uploads", x => x.UploadId);
                });

            migrationBuilder.CreateTable(
                name: "Projects",
                columns: table => new
                {
                    ProjectId = table.Column<int>(nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    ProjectUid = table.Column<string>(nullable: true),
                    Name = table.Column<string>(nullable: true),
                    HydroSystemId = table.Column<int>(nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Projects", x => x.ProjectId);
                    table.ForeignKey(
                        name: "FK_Projects_HydroSystems_HydroSystemId",
                        column: x => x.HydroSystemId,
                        principalTable: "HydroSystems",
                        principalColumn: "HydroSystemId",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "Reservoirs",
                columns: table => new
                {
                    ReservoirId = table.Column<int>(nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    ReservoirUid = table.Column<string>(nullable: true),
                    HydroSystemId = table.Column<int>(nullable: false),
                    Name = table.Column<string>(nullable: true),
                    MinVolume = table.Column<double>(nullable: false),
                    MaxVolume = table.Column<double>(nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Reservoirs", x => x.ReservoirId);
                    table.ForeignKey(
                        name: "FK_Reservoirs_HydroSystems_HydroSystemId",
                        column: x => x.HydroSystemId,
                        principalTable: "HydroSystems",
                        principalColumn: "HydroSystemId",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "Forecasts",
                columns: table => new
                {
                    ForecastId = table.Column<int>(nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    ForecastUid = table.Column<string>(nullable: true),
                    UploadId = table.Column<int>(nullable: false),
                    HydroSystemId = table.Column<int>(nullable: false),
                    Name = table.Column<string>(nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Forecasts", x => x.ForecastId);
                    table.ForeignKey(
                        name: "FK_Forecasts_HydroSystems_HydroSystemId",
                        column: x => x.HydroSystemId,
                        principalTable: "HydroSystems",
                        principalColumn: "HydroSystemId",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_Forecasts_Uploads_UploadId",
                        column: x => x.UploadId,
                        principalTable: "Uploads",
                        principalColumn: "UploadId",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "TimeDataSeries",
                columns: table => new
                {
                    TimeDataSeriesId = table.Column<int>(nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    UploadId = table.Column<int>(nullable: false),
                    StartTime = table.Column<DateTimeOffset>(nullable: false),
                    EndTime = table.Column<DateTimeOffset>(nullable: false),
                    Description = table.Column<string>(nullable: true),
                    Type = table.Column<int>(nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_TimeDataSeries", x => x.TimeDataSeriesId);
                    table.ForeignKey(
                        name: "FK_TimeDataSeries_Uploads_UploadId",
                        column: x => x.UploadId,
                        principalTable: "Uploads",
                        principalColumn: "UploadId",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "SeriesLinks",
                columns: table => new
                {
                    TimeDataSeriesLinkId = table.Column<int>(nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    UploadId = table.Column<int>(nullable: false),
                    ForecastId = table.Column<int>(nullable: false),
                    InflowSeriesId = table.Column<int>(nullable: false),
                    PriceSeriesId = table.Column<int>(nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_SeriesLinks", x => x.TimeDataSeriesLinkId);
                    table.ForeignKey(
                        name: "FK_SeriesLinks_Forecasts_ForecastId",
                        column: x => x.ForecastId,
                        principalTable: "Forecasts",
                        principalColumn: "ForecastId",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_SeriesLinks_Uploads_UploadId",
                        column: x => x.UploadId,
                        principalTable: "Uploads",
                        principalColumn: "UploadId",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "TimeDataValue",
                columns: table => new
                {
                    TimeDataSeriesId = table.Column<int>(nullable: false),
                    TimeStampOffset = table.Column<DateTimeOffset>(nullable: false),
                    Value = table.Column<double>(nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_TimeDataValue", x => new { x.TimeDataSeriesId, x.TimeStampOffset });
                    table.ForeignKey(
                        name: "FK_TimeDataValue_TimeDataSeries_TimeDataSeriesId",
                        column: x => x.TimeDataSeriesId,
                        principalTable: "TimeDataSeries",
                        principalColumn: "TimeDataSeriesId",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "AgentControls",
                columns: table => new
                {
                    AgentControlId = table.Column<int>(nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    AgentId = table.Column<int>(nullable: false),
                    Signal = table.Column<int>(nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_AgentControls", x => x.AgentControlId);
                });

            migrationBuilder.CreateTable(
                name: "EvaluationEpisodes",
                columns: table => new
                {
                    EvaluationEpisodeId = table.Column<int>(nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    ProjectRunId = table.Column<int>(nullable: false),
                    Description = table.Column<string>(nullable: true),
                    AgentId = table.Column<int>(nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_EvaluationEpisodes", x => x.EvaluationEpisodeId);
                });

            migrationBuilder.CreateTable(
                name: "ReportData",
                columns: table => new
                {
                    ReportSeriesId = table.Column<int>(nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    StartTime = table.Column<DateTimeOffset>(nullable: false),
                    EndTime = table.Column<DateTimeOffset>(nullable: true),
                    Description = table.Column<string>(nullable: true),
                    Type = table.Column<string>(nullable: true),
                    EvaluationEpisodeId = table.Column<int>(nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ReportData", x => x.ReportSeriesId);
                    table.ForeignKey(
                        name: "FK_ReportData_EvaluationEpisodes_EvaluationEpisodeId",
                        column: x => x.EvaluationEpisodeId,
                        principalTable: "EvaluationEpisodes",
                        principalColumn: "EvaluationEpisodeId",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "ReportValues",
                columns: table => new
                {
                    ReportSeriesId = table.Column<int>(nullable: false),
                    Step = table.Column<int>(nullable: false),
                    Index = table.Column<int>(nullable: false),
                    TimeStamp = table.Column<DateTimeOffset>(nullable: false),
                    Value = table.Column<double>(nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ReportValues", x => new { x.ReportSeriesId, x.Step, x.Index });
                    table.ForeignKey(
                        name: "FK_ReportValues_ReportData_ReportSeriesId",
                        column: x => x.ReportSeriesId,
                        principalTable: "ReportData",
                        principalColumn: "ReportSeriesId",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "ProjectRuns",
                columns: table => new
                {
                    ProjectRunId = table.Column<int>(nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    ProjectRunGuid = table.Column<string>(nullable: true),
                    ProjectId = table.Column<int>(nullable: false),
                    StartTime = table.Column<DateTimeOffset>(nullable: true),
                    EndTime = table.Column<DateTimeOffset>(nullable: true),
                    ForecastId = table.Column<int>(nullable: false),
                    Settings = table.Column<string>(nullable: true),
                    ApiSettings = table.Column<string>(nullable: true),
                    Comment = table.Column<string>(nullable: true),
                    EvaluatedOn = table.Column<int>(nullable: true),
                    PreviousProjectRunId = table.Column<int>(nullable: true),
                    PreviousQValueProjectRunId = table.Column<int>(nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ProjectRuns", x => x.ProjectRunId);
                    table.ForeignKey(
                        name: "FK_ProjectRuns_Forecasts_ForecastId",
                        column: x => x.ForecastId,
                        principalTable: "Forecasts",
                        principalColumn: "ForecastId",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_ProjectRuns_ProjectRuns_PreviousProjectRunId",
                        column: x => x.PreviousProjectRunId,
                        principalTable: "ProjectRuns",
                        principalColumn: "ProjectRunId",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_ProjectRuns_ProjectRuns_PreviousQValueProjectRunId",
                        column: x => x.PreviousQValueProjectRunId,
                        principalTable: "ProjectRuns",
                        principalColumn: "ProjectRunId",
                        onDelete: ReferentialAction.Restrict);
                    table.ForeignKey(
                        name: "FK_ProjectRuns_Projects_ProjectId",
                        column: x => x.ProjectId,
                        principalTable: "Projects",
                        principalColumn: "ProjectId",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "Agents",
                columns: table => new
                {
                    AgentId = table.Column<int>(nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    AgentUid = table.Column<string>(nullable: true),
                    ProjectId = table.Column<int>(nullable: false),
                    ProjectRunId = table.Column<int>(nullable: false),
                    Seed = table.Column<int>(nullable: false),
                    BestModelPath = table.Column<string>(nullable: true),
                    StartTime = table.Column<DateTimeOffset>(nullable: false),
                    EndTime = table.Column<DateTimeOffset>(nullable: true),
                    Ancestor = table.Column<int>(nullable: true),
                    BestStep = table.Column<int>(nullable: true),
                    BestStepValue = table.Column<double>(nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Agents", x => x.AgentId);
                    table.ForeignKey(
                        name: "FK_Agents_Projects_ProjectId",
                        column: x => x.ProjectId,
                        principalTable: "Projects",
                        principalColumn: "ProjectId",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_Agents_ProjectRuns_ProjectRunId",
                        column: x => x.ProjectRunId,
                        principalTable: "ProjectRuns",
                        principalColumn: "ProjectRunId",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "ProjectRunControls",
                columns: table => new
                {
                    ProjectRunControlId = table.Column<int>(nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    ProjectRunId = table.Column<int>(nullable: false),
                    Signal = table.Column<int>(nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ProjectRunControls", x => x.ProjectRunControlId);
                    table.ForeignKey(
                        name: "FK_ProjectRunControls_ProjectRuns_ProjectRunId",
                        column: x => x.ProjectRunId,
                        principalTable: "ProjectRuns",
                        principalColumn: "ProjectRunId",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "ProjectRunStartVolume",
                columns: table => new
                {
                    ProjectRunStartVolumeId = table.Column<int>(nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    ProjectRunId = table.Column<int>(nullable: false),
                    ReservoirId = table.Column<int>(nullable: false),
                    Value = table.Column<double>(nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ProjectRunStartVolume", x => x.ProjectRunStartVolumeId);
                    table.ForeignKey(
                        name: "FK_ProjectRunStartVolume_ProjectRuns_ProjectRunId",
                        column: x => x.ProjectRunId,
                        principalTable: "ProjectRuns",
                        principalColumn: "ProjectRunId",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_ProjectRunStartVolume_Reservoirs_ReservoirId",
                        column: x => x.ReservoirId,
                        principalTable: "Reservoirs",
                        principalColumn: "ReservoirId",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "TrainStepData",
                columns: table => new
                {
                    StepSeriesId = table.Column<int>(nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    StartTime = table.Column<DateTimeOffset>(nullable: false),
                    EndTime = table.Column<DateTimeOffset>(nullable: true),
                    Description = table.Column<string>(nullable: true),
                    Type = table.Column<string>(nullable: true),
                    AgentId = table.Column<int>(nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_TrainStepData", x => x.StepSeriesId);
                    table.ForeignKey(
                        name: "FK_TrainStepData_Agents_AgentId",
                        column: x => x.AgentId,
                        principalTable: "Agents",
                        principalColumn: "AgentId",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "TrainStepValues",
                columns: table => new
                {
                    StepSeriesId = table.Column<int>(nullable: false),
                    Step = table.Column<int>(nullable: false),
                    TimeStamp = table.Column<DateTimeOffset>(nullable: false),
                    Value = table.Column<double>(nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_TrainStepValues", x => new { x.StepSeriesId, x.Step });
                    table.ForeignKey(
                        name: "FK_TrainStepValues_TrainStepData_StepSeriesId",
                        column: x => x.StepSeriesId,
                        principalTable: "TrainStepData",
                        principalColumn: "StepSeriesId",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_AgentControls_AgentId",
                table: "AgentControls",
                column: "AgentId");

            migrationBuilder.CreateIndex(
                name: "IX_Agents_ProjectId",
                table: "Agents",
                column: "ProjectId");

            migrationBuilder.CreateIndex(
                name: "IX_Agents_ProjectRunId",
                table: "Agents",
                column: "ProjectRunId");

            migrationBuilder.CreateIndex(
                name: "IX_EvaluationEpisodes_AgentId",
                table: "EvaluationEpisodes",
                column: "AgentId");

            migrationBuilder.CreateIndex(
                name: "IX_EvaluationEpisodes_ProjectRunId",
                table: "EvaluationEpisodes",
                column: "ProjectRunId");

            migrationBuilder.CreateIndex(
                name: "IX_Forecasts_HydroSystemId",
                table: "Forecasts",
                column: "HydroSystemId");

            migrationBuilder.CreateIndex(
                name: "IX_Forecasts_UploadId",
                table: "Forecasts",
                column: "UploadId");

            migrationBuilder.CreateIndex(
                name: "IX_ProjectRunControls_ProjectRunId",
                table: "ProjectRunControls",
                column: "ProjectRunId");

            migrationBuilder.CreateIndex(
                name: "IX_ProjectRuns_EvaluatedOn",
                table: "ProjectRuns",
                column: "EvaluatedOn");

            migrationBuilder.CreateIndex(
                name: "IX_ProjectRuns_ForecastId",
                table: "ProjectRuns",
                column: "ForecastId");

            migrationBuilder.CreateIndex(
                name: "IX_ProjectRuns_PreviousProjectRunId",
                table: "ProjectRuns",
                column: "PreviousProjectRunId");

            migrationBuilder.CreateIndex(
                name: "IX_ProjectRuns_PreviousQValueProjectRunId",
                table: "ProjectRuns",
                column: "PreviousQValueProjectRunId");

            migrationBuilder.CreateIndex(
                name: "IX_ProjectRuns_ProjectId",
                table: "ProjectRuns",
                column: "ProjectId");

            migrationBuilder.CreateIndex(
                name: "IX_ProjectRunStartVolume_ProjectRunId",
                table: "ProjectRunStartVolume",
                column: "ProjectRunId");

            migrationBuilder.CreateIndex(
                name: "IX_ProjectRunStartVolume_ReservoirId",
                table: "ProjectRunStartVolume",
                column: "ReservoirId");

            migrationBuilder.CreateIndex(
                name: "IX_Projects_HydroSystemId",
                table: "Projects",
                column: "HydroSystemId");

            migrationBuilder.CreateIndex(
                name: "IX_Projects_Name",
                table: "Projects",
                column: "Name",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_ReportData_EvaluationEpisodeId",
                table: "ReportData",
                column: "EvaluationEpisodeId");

            migrationBuilder.CreateIndex(
                name: "IX_Reservoirs_HydroSystemId",
                table: "Reservoirs",
                column: "HydroSystemId");

            migrationBuilder.CreateIndex(
                name: "IX_SeriesLinks_ForecastId",
                table: "SeriesLinks",
                column: "ForecastId");

            migrationBuilder.CreateIndex(
                name: "IX_SeriesLinks_UploadId",
                table: "SeriesLinks",
                column: "UploadId");

            migrationBuilder.CreateIndex(
                name: "IX_TimeDataSeries_UploadId",
                table: "TimeDataSeries",
                column: "UploadId");

            migrationBuilder.CreateIndex(
                name: "IX_TrainStepData_AgentId",
                table: "TrainStepData",
                column: "AgentId");

            migrationBuilder.AddForeignKey(
                name: "FK_AgentControls_Agents_AgentId",
                table: "AgentControls",
                column: "AgentId",
                principalTable: "Agents",
                principalColumn: "AgentId",
                onDelete: ReferentialAction.Cascade);

            migrationBuilder.AddForeignKey(
                name: "FK_EvaluationEpisodes_Agents_AgentId",
                table: "EvaluationEpisodes",
                column: "AgentId",
                principalTable: "Agents",
                principalColumn: "AgentId",
                onDelete: ReferentialAction.Cascade);

            migrationBuilder.AddForeignKey(
                name: "FK_EvaluationEpisodes_ProjectRuns_ProjectRunId",
                table: "EvaluationEpisodes",
                column: "ProjectRunId",
                principalTable: "ProjectRuns",
                principalColumn: "ProjectRunId",
                onDelete: ReferentialAction.Cascade);

            migrationBuilder.AddForeignKey(
                name: "FK_ProjectRuns_Agents_EvaluatedOn",
                table: "ProjectRuns",
                column: "EvaluatedOn",
                principalTable: "Agents",
                principalColumn: "AgentId",
                onDelete: ReferentialAction.Restrict);
        }

        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_ProjectRuns_Agents_EvaluatedOn",
                table: "ProjectRuns");

            migrationBuilder.DropTable(
                name: "AgentControls");

            migrationBuilder.DropTable(
                name: "ProjectRunControls");

            migrationBuilder.DropTable(
                name: "ProjectRunStartVolume");

            migrationBuilder.DropTable(
                name: "ReportValues");

            migrationBuilder.DropTable(
                name: "SeriesLinks");

            migrationBuilder.DropTable(
                name: "TimeDataValue");

            migrationBuilder.DropTable(
                name: "TrainStepValues");

            migrationBuilder.DropTable(
                name: "Reservoirs");

            migrationBuilder.DropTable(
                name: "ReportData");

            migrationBuilder.DropTable(
                name: "TimeDataSeries");

            migrationBuilder.DropTable(
                name: "TrainStepData");

            migrationBuilder.DropTable(
                name: "EvaluationEpisodes");

            migrationBuilder.DropTable(
                name: "Agents");

            migrationBuilder.DropTable(
                name: "ProjectRuns");

            migrationBuilder.DropTable(
                name: "Forecasts");

            migrationBuilder.DropTable(
                name: "Projects");

            migrationBuilder.DropTable(
                name: "Uploads");

            migrationBuilder.DropTable(
                name: "HydroSystems");
        }
    }
}
