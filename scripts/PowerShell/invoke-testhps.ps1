$Url = "http://lucifer:5400/api/v1"

#Get Hydrosystems:
$Hydrosystems = Invoke-RestMethod -Uri "$Url/hydrosystems" -Method GET -UseBasicParsing


#Choose flørli:
$Flørli = $Hydrosystems | where-object {$_.name -eq "Flørli"}


#Get Reservoirs
$Uri = "$Url/hydrosystems/$($Flørli.Uid)/reservoirs"
$Reservoirs = Invoke-RestMethod -Uri $Uri -Method GET -UseBasicParsing


#Get Forecasts
$Uri = "$Url/hydrosystems/$($Flørli.Uid)/forecasts"
$Forecasts = Invoke-RestMethod -Uri $Uri -Method GET -UseBasicParsing

#choose first forecast
$Forecast = $Forecasts | where-object {$_.name -eq "NVE Spot forecast"}


#Get Scenarios
$Uri = "$Url/forecasts/$($Forecast.uid)"
$Scenarios = Invoke-RestMethod -Uri $Uri -Method GET -UseBasicParsing

#Choose scenario
$ScenarioName = $Scenarios.scenarios[0]


$Uri = "$Url/forecasts/$($Forecast.uid)/scenarios/$($ScenarioName)"
$ScenarioData = Invoke-RestMethod -Uri $Uri -Method GET -UseBasicParsing


#Create new Project
$ProjectName = New-Guid
$Uri = "$Url/projects?name=$ProjectName&hydrosystemUid=$($Flørli.uid)"
$Project = Invoke-RestMethod -Uri $Uri -Method POST -UseBasicParsing


#Get Project
$Uri = "$Url/projects"
$ProjectCheck = (Invoke-RestMethod -Uri $Uri -Method GET -UseBasicParsing) | where-object {$_.uid -eq $project.uid}
if(Compare-object -ReferenceObject $ProjectCheck -DifferenceObject $Project){
    throw "Project recieved from POST not equal to project from GET"
}

$Uri = "$Url/projects/$($Project.uid)/runsettingstemplate"
$RunSettingsTemplate = Invoke-RestMethod -Uri $Uri -Method GET -UseBasicParsing

#Run Project
$RunSettingsJson = $RunSettingsTemplate | ConvertTo-Json
$Uri = "$Url/projects/$($Project.uid)/run?forecastUid=$($Forecast.uid)"
$ProjectRunResponse = Invoke-RestMethod -Uri $Uri -Method PUT -Body ([System.Text.Encoding]::UTF8.GetBytes($RunSettingsJson)) -UseBasicParsing -header @{"Content-Type" = "application/json"}
$ProjectRun = $ProjectRunResponse.Content | ConvertFrom-Json

#Stop Project
$Uri = "$Url/projectruns​/$($ProjectRun.uid)​/terminate"
$ProjectStop = invoke-WebRequest -Uri $Uri -Method PUT -UseBasicParsing

#Missing member Json
$RunSettingsCopy = ($RunSettingsJson | ConvertFrom-Json)
$RunSettingsCopy | Add-Member -MemberType "NoteProperty" -Name "Foo" -Value "Bar"
$RunSettingsJson = $RunSettingsCopy | ConvertTo-Json -Depth 5
$Uri = "$Url/projects/$($Project.uid)/run?forecastUid=$($Forecast.uid)"
$ProjectFailRun = Invoke-WebRequest -Uri $Uri -Method PUT -Body ([System.Text.Encoding]::UTF8.GetBytes($RunSettingsJson)) -UseBasicParsing -header @{"Content-Type" = "application/json"}