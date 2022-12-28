# Web API


Below is the documentation for the HydroRL Web API. Furthermore, a swagger client is available to interact with the API for development purposes. It is available at endpoint /swagger on port 5400 at the machine hosting the API ('host-machine':5400/swagger.).


## Concepts

```{figure} ./img/HPS_API_Concepts.png
:name: api-concepts

Illustration of the main concepts in the Web API. 
```

The above illustration shows the dependencies between the main concepts of the API. In order to run a training one has to define a hydro power system and a forecast to train on. There are API endpoints to view and load forecast. A training is executed in the context of a project run, where a given project can have many project runs. To create a project one has to define a hydro system. 

After a succesfull project run, one can use the trained model from a given project run and perform an evaluation. The evaluation can then be run with different settings and/or with another forecast. 


## Documentation

```{eval-rst}
.. openapi:: api.yml
    :examples:
    :format: markdown
```

