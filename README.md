# The HydroRL Application

## Project Description
The HydroRL is a reinforcement learning based model to perform hydropower scheduling. It has packages to construct hydro power systems and running Stable Baselines3 (SB3) based RL algorithms. 

The problem we are trying to solve is to maximize the utilization of the hydropower system, which is modelled by reservoirs, power stations, gates and connections between them. The model requires a forecast of energy prices and inflows to the reservoirs. Based on those forecasts and the required configuration (time horizon, end value, etc.) the model aims at maximizing the expected reward of the specified time horizon.

For problems with weekly time resolutions we managed to get comparable results as to another model based on Stochastic Dual Dynamic Programming (SDDP), used commercially by hydropower companies. This was also the case for more complex hydropower systems, with multiple waterways, reservoirs and power stations. 

For problems where we increased the time resolution, from daily to hourly we observed that the model struggled with converging. We tried a variety of hyperparameter tuning, reward function tuning, splitting the problem into a short-term (hourly) and long-term (weekly) model but where not able to obtain comparable results as 

Note that in an earlier version we used Tensorflow Agents as the RL engine, we found it hard to work with so we started using SB3 instead. 


## Overview

Below is an overview of the different components of the HydroRL application.

![HydroRL Overview](media/HPS-MVP1.png)

For more details on the stack and different components see [SYSTEM_OVERVIEW](SYSTEM_OVERVIEW).

### Steps for running the project
The HydroRL application consist of one flask application that consist of the business layer, an application server that hosts the client facing API written in .NET Core, and the sqlite database.

The following describes the initialization of the application

1. Start the web app
    - This will also build  the HPSDB.db sqlite database file. 
2. Start the flask server
3. Migration built?
4. Copy appsettings.json to appsettings.Development.json
    - Change {PATH} in appsettings.Development.json to required path for databases
5. Popoulate the db with data.
    - Run `python scripts/insert_hydro_system_to_db.py`, to add hydro systems.
    - Run `python scripts/insert_example_forecasts_to_db.py`, to add example forecasts to db. 


## Usage
The easiest way to get started is to start the application with [docker compose](https://docs.docker.com/compose/), follow [these](https://docs.docker.com/compose/install/) instructions to install it. This takes cares of all the nitty details and ensures you have an running application.

After docker composed is installed, clone this repo:
```
git clone https://github.com/Fraktal-Norge-AS/HydroRL.git
```

Build the docker containers (note that this might take a couple of minutes):
```
docker compose build
```

Run the application
```
docker compose up
```


### VS Code Misc.

The namespace of the package is fairly large. By default Ubuntu can watch 8192 file handles. If the notification <em>"Visual Studio Code is unable to watch for file changes in this large workspace"</em> pops up, add ```fs.inotify.max_user_watches=100000``` or any number up to 524 288 at the bottom of the file ```/etc/sysctl.conf```. Load the new values by running ```sudo sysctl -p```.


## Example

```python
code
```
Output:


## Build and Test


### Build web API documentation into the sphinx documentation
To build yaml file with swagger documentation, follow the steps provided [here](https://medium.com/@woeterman_94/how-to-generate-a-swagger-json-file-on-build-in-net-core-fa74eec3df1).

With the Swashbuckle CLI tool installed, run the following
```
ASPNETCORE_ENVIRONMENT=Development swagger tofile --yaml --output ../docs/source/api.yml bin/Debug/netcoreapp2.2/DKWebapp.dll v1
```


## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgement
We would like to thank Sindre Tøsse, Vegard Kyllingstad and Øyivind Høivik at Lyse Produksjon AS for providing data and feedback to the project. 

Team members at Fraktal involved on the project:
 - Jan Ivar Kjøde
 - Lars Kartevoll
 - Martin Hjelmeland
 - Stian Bakke
 - Siv Sødal