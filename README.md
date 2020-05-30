# COVID-19 Dashboard

Simple dashboard with COVID-19 global and separate Russian Federation statistics on [Dash](https://plotly.com/dash/), a Python framework for building analytical web applications. The completed app was deployed on [Heroku](https://www.heroku.com/home) and can be viewed at <https://covid19-dash-prod.herokuapp.com/>

![gif here](assets/pres.gif)

## Installation

### Docker

    docker run -d -p 8050:8050 lightblash/covid19_dash:v0.1

and visit <http://127.0.0.1:8050/> in your web browser. You should see the app.

### Clone

Clone this repository to your local machine running one of the following commands

via SSH

    git clone git@github.com:Lightblash/covid19-dashboard.git

via HTTPS

    git clone https://github.com/Lightblash/covid19-dashboard.git

### Setup

Install all dependencies into your current environment running the following command from the root of repo

    pip install -r requirements.txt

## How to use

Run the app from the root directory of the repo with

    python covid19_dashboard.py

and visit <http://127.0.0.1:8050/> in your web browser. You should see the app.

## License

This project is licensed under the terms of the MIT license
