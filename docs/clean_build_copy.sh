#!/bin/bash
# Copy notebooks to docs/source/notebooks so sphinx can parse them.
cp ../notebooks/APIdemo/ForecastExample.ipynb source/notebooks/ForecastExample.ipynb
cp ../notebooks/APIdemo/GettingStarted.ipynb source/notebooks/GettingStarted.ipynb
cp ../notebooks/APIdemo/StochasticVariables.ipynb source/notebooks/StochasticVariables.ipynb

make clean
make html
cp -r build /media/data/hydro_scheduling/sphinx-documentation/

file="/media/data/hydro_scheduling/sphinx-documentation/build/html/notebooks/plotly.js"
if [ -e "$file" ]; then
    echo "plotly.js exists"
else 
    wget -O /media/data/hydro_scheduling/sphinx-documentation/build/html/notebooks/plotly.js https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.3.1/plotly.min.js
fi 