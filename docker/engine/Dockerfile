FROM pytorch/pytorch:1.13.1-cuda11.6-cudnn8-runtime

EXPOSE 5678

RUN apt-get update \
    && apt-get dist-upgrade -y --no-install-recommends \
    && apt-get install -y --no-install-recommends \
    apt-utils \
    graphviz \
    graphviz-dev \
    python3-dev \
    build-essential

WORKDIR /static/

COPY ./requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=/static/server/app.py

COPY ./webapp/appsettings.json ./webapp/appsettings.Development.json
RUN sed -i 's+{PATH}+/hps_server/+g' ./webapp/appsettings.Development.json

CMD [ "python", "-m" , "flask", "run", "--no-debugger", "--no-reload", "--host", "0.0.0.0", "--port", "5678", "--without-threads"]