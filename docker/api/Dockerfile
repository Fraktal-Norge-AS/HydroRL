FROM mcr.microsoft.com/dotnet/core/sdk:2.2-bionic
WORKDIR /appdir
EXPOSE 80
EXPOSE 5400

COPY ./webapp/*.csproj ./
RUN dotnet restore

COPY ./webapp ./
RUN dotnet publish -c Release -o out

COPY ./webapp/appsettings.json ./appsettings.Development.json
RUN sed -i 's+{PATH}+/hps_server/+g' ./appsettings.Development.json
RUN mkdir /hps_server

# Map to the IP of the docker hosting the flask server
RUN sed -i 's+127.0.0.1:5678+flaskengine:5678+g' ./appsettings.Development.json 

ENV ASPNETCORE_ENVIRONMENT=Development

ENTRYPOINT ["dotnet", "out/DKWebapp.dll"]