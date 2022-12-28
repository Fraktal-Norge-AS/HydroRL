# The HydroRL Package

## Project Description
The HydroRL is a reinforcement learning based model to perform hydropower scheduling. It has packages to construct hydro power systems and running Stable Baselines3 based RL algorithms. 


- What does it do?
- Why you used the technology you did
- Some challanges you met and features to implement in the future


## Getting Started


### Software dependencies
The package has been developed in a conda environment described in `./tfa_conda_env.yml'. The conda environment can be set up as following:

From your home dir
 1. Download miniconda distribution. Run `wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh`
 2. Install miniconda. Run `bash Miniconda3-latest-Linux-x86_64.sh`
    - Enter to accept installation on your home directory
    - Promt yes to run conda init
    - Restart the shell.
 3. Run `conda env create -f {repo_dir}/tfa_conda_env.yml`, where `{repo_dir}` is the path to this repository.
        - This creates a conda environment called `tfa22` with additional dependencies.
 4. Run `conda activate tfa22`

#### Install .NET

It was a problem with some of the packages related to entity framework, to avoid this we ran an older version of .NET. To install it, run the following
```
sudo apt-get update && \
  sudo apt-get install -y dotnet-sdk-2.2
```
See [Microsoft documentation](https://learn.microsoft.com/en-us/dotnet/core/install/linux-ubuntu) for more information.


### Run the project
Explain how to run it and how to use it

- Start the flask server
- Start the web app
  - This will also build the db
- Popoulate the db with data. To do this you can use the code in scripts/load_nve_forecast_to_db.py. This will collect historical inflows from the NVE api that can be used as scenarios. Note that for energy price you will have to write your own function to collect them. The db should also be populated with hydro systems. This is done by running insert_hydro_system_to_db.py in scripts/.
 


### VS Code Misc.

The namespace of the package is fairly large. By default Ubuntu can watch 8192 file handles. If the notification <em>"Visual Studio Code is unable to watch for file changes in this large workspace"</em> pops up, add ```fs.inotify.max_user_watches=100000``` or any number up to 524 288 at the bottom of the file ```/etc/sysctl.conf```. Load the new values by running ```sudo sysctl -p```.

### Solvers

Install cbc solver with ```sudo apt-get install coinor-cbc```, available [here](https://ubuntu.pkgs.org/20.10/ubuntu-universe-armhf/coinor-libcbc-dev_2.10.5+ds1-1_armhf.deb.html). Check that the version is up to date (v2.10+). If not, build the cbc package from source using [coinbrew](https://coin-or.github.io/coinbrew/).


## Example

```python
code
```
Output:


## Build and Test


### Build web API documentation
To build yaml file with swagger documentation, follow the steps provided [here](https://medium.com/@woeterman_94/how-to-generate-a-swagger-json-file-on-build-in-net-core-fa74eec3df1).

With the Swashbuckle CLI tool installed, run the following
```
ASPNETCORE_ENVIRONMENT=Development swagger tofile --yaml --output ../docs/source/api.yml bin/Debug/netcoreapp2.2/DKWebapp.dll v1
````
