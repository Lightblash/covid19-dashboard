# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

CONFIRMED_CSV = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'

RECOVERED_CSV = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'

DEATHS_CSV = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'


def get_metric_ser(metric_csv, metric_type, country=None):
    """

        Parameter
        ---------

        metrics_csv : url
            Full url path to target csv file

        metric_type : str
            One of ['cumulative', 'new']

        country : str
            If None global stats is provided
    """

    df = pd.read_csv(metric_csv)
    df.drop(columns=['Province/State'], inplace=True)
    df = df.melt(
        id_vars=['Country/Region', 'Lat', 'Long'],
        var_name='date',
        value_name='value'
    )
    df['date'] = pd.to_datetime(df['date'])
    df = df.groupby(['Country/Region', 'date']).value.sum().reset_index()
    df['prev_value'] = df.groupby('Country/Region').value.shift(1)
    df['new_cases'] = df.value - df.prev_value

    if not country:
        if metric_type == 'cumulative':
            return df.groupby('date').value.sum()
        if metric_type == 'new':
            return df.groupby('date').new_cases.sum()
    if country:
        if metric_type == 'cumulative':
            return df[df['Country/Region'] == country].groupby('date').value.sum()
        if metric_type == 'new':
            return df[df['Country/Region'] == country].groupby('date').new_cases.sum()


# confirmed
global_confirmed_cum = get_metric_ser(CONFIRMED_CSV, 'cumulative')
global_confirmed_new = get_metric_ser(CONFIRMED_CSV, 'new')
rus_confirmed_cum = get_metric_ser(CONFIRMED_CSV, 'cumulative', 'Russia')
rus_new_cases = get_metric_ser(CONFIRMED_CSV, 'new', 'Russia')

# recovered
global_recovered_cum = get_metric_ser(RECOVERED_CSV, 'cumulative')
global_new_recovered = get_metric_ser(RECOVERED_CSV, 'new')
rus_recovered_cum = get_metric_ser(RECOVERED_CSV, 'cumulative', 'Russia')
rus_new_recovered = get_metric_ser(RECOVERED_CSV, 'new', 'Russia')

# deaths
global_deaths_cum = get_metric_ser(DEATHS_CSV, 'cumulative')
global_new_deaths = get_metric_ser(DEATHS_CSV, 'new')
rus_deaths_cum = get_metric_ser(DEATHS_CSV, 'cumulative', 'Russia')
rus_new_deaths = get_metric_ser(DEATHS_CSV, 'new', 'Russia')

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#FFFFFF',
    'text': '#8C9D95'
}


def serve_layout():
    return html.Div(
        [
            html.H1('COVID-19 Dashboard'),
            html.Div(
                [
                    html.Button('Cumulative', id='cum_button', n_clicks_timestamp=1),
                    html.Button('New Cases', id='new_cases_button', n_clicks_timestamp=0)
                ],
                style={'textAlign': 'center'}
            ),
            html.Div(
                id='button-clicked',
                style={'textAlign': 'center'}
            ),
            dcc.Tabs(id="tabs", value='rus_tab', children=[
                dcc.Tab(label='Russia', value='rus_tab'),
                dcc.Tab(label='World', value='global_tab'),
            ]),
            html.Div(id='tabs-content'),
        ]
    )


def generate_plot(x, y, type, title, color):
    return dcc.Graph(
        # id='articles_id',
        figure={
            'data': [
                {
                    'x': x,
                    'y': y,
                    'type': type, 'name': title,
                    'marker': {'color': color}
                }
            ],
            'layout': {
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'font': {'color': 'green'},
                'color': 'green',
                'title': title
            }
        }
    )


def render_rus_cumulative_content():
    """
        Render Russian cumulative stats
    """
    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=rus_confirmed_cum.values[-1],
        number={"valueformat": "9,999,999"},
        domain={'x': [0, 0.33], 'y': [0, 0.5]},
        title={'text': 'Confirmed'},
        delta={
            'reference': rus_confirmed_cum.values[-2],
            'relative': False,
            'position': "bottom",
            'valueformat': "#,###",
            'increasing.color': 'blue',
            'increasing.symbol': '+',
        }))

    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=rus_recovered_cum.values[-1],
        number={"valueformat": "9,999,999"},
        domain={'x': [0.33, 0.66], 'y': [0, 0.5]},
        title={'text': 'Recovered'},
        delta={
            'reference': rus_recovered_cum.values[-2],
            'relative': False,
            'position': "bottom",
            'valueformat': "#,###",
            'increasing.color': 'green',
            'increasing.symbol': '+'
        }))

    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=rus_deaths_cum.values[-1],
        number={"valueformat": "9,999,999"},
        domain={'x': [0.66, 1], 'y': [0, 0.5]},
        title={'text': 'Deaths'},
        delta={
            'reference': rus_deaths_cum.values[-2],
            'relative': False,
            'position': "bottom",
            'valueformat': "#,###",
            'increasing.color': 'red',
            'increasing.symbol': '+'
        }))

    return html.Div(children=[
        html.Div(
            [
                dcc.Graph(figure=fig),
            ]
        ),
        html.H2(
            children='Confirmed Cases',
            style={
                'textAlign': 'right',
                'color': colors['text']
            }
        ),
        generate_plot(
            x=rus_confirmed_cum.index,
            y=rus_confirmed_cum.values,
            type='bar',
            title='Confirmed Cases',
            color='blue'
        ),
        html.H2(
            children='Recovered',
            style={
                'textAlign': 'right',
                'color': colors['text']
            }
        ),
        generate_plot(
            x=rus_recovered_cum.index,
            y=rus_recovered_cum.values,
            type='bar',
            title='Recovered',
            color='green'
        ),
        html.H2(
            children='Deaths',
            style={
                'textAlign': 'right',
                'color': colors['text']
            }
        ),
        generate_plot(
            x=rus_deaths_cum.index,
            y=rus_deaths_cum.values,
            type='bar',
            title='Deaths',
            color='red'
        ),
    ])


def render_rus_new_content():
    """
        Render Russian new stats
    """
    return html.Div(children=[
        html.H2(
            children='New Cases',
            style={
                'textAlign': 'right',
                'color': colors['text']
            }
        ),
        generate_plot(
            x=rus_new_cases.index,
            y=rus_new_cases.values,
            type='bar',
            title='New Cases',
            color='blue'
        ),
        html.H2(
            children='New Recovered',
            style={
                'textAlign': 'right',
                'color': colors['text']
            }
        ),
        generate_plot(
            x=rus_new_recovered.index,
            y=rus_new_recovered.values,
            type='bar',
            title='New Recovered',
            color='green'
        ),
        html.H2(
            children='New Deaths',
            style={
                'textAlign': 'right',
                'color': colors['text']
            }
        ),
        generate_plot(
            x=rus_new_deaths.index,
            y=rus_new_deaths.values,
            type='bar',
            title='New Deaths',
            color='red'
        ),
    ])


def render_global_cumulative_content():
    """
        Render worldwide cumulative stats
    """

    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=global_confirmed_cum.values[-1],
        number={"valueformat": "9,999,999"},
        domain={'x': [0, 0.33], 'y': [0, 0.5]},
        title={'text': 'Confirmed'},
        delta={
            'reference': global_confirmed_cum.values[-2],
            'relative': False,
            'position': "bottom",
            'valueformat': "#,###",
            'increasing.color': 'blue',
            'increasing.symbol': '+',
        }))

    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=global_recovered_cum.values[-1],
        number={"valueformat": "9,999,999"},
        domain={'x': [0.33, 0.66], 'y': [0, 0.5]},
        title={'text': 'Recovered'},
        delta={
            'reference': global_recovered_cum.values[-2],
            'relative': False,
            'position': "bottom",
            'valueformat': "#,###",
            'increasing.color': 'green',
            'increasing.symbol': '+'
        }))

    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=global_deaths_cum.values[-1],
        number={"valueformat": "9,999,999"},
        domain={'x': [0.66, 1], 'y': [0, 0.5]},
        title={'text': 'Deaths'},
        delta={
            'reference': global_deaths_cum.values[-2],
            'relative': False,
            'position': "bottom",
            'valueformat': "#,###",
            'increasing.color': 'red',
            'increasing.symbol': '+'
        }))

    return html.Div(children=[
        html.Div(
            [
                dcc.Graph(figure=fig),
            ]
        ),
        html.H2(
            children='Confirmed Cases',
            style={
                'textAlign': 'right',
                'color': colors['text']
            }
        ),
        generate_plot(
            x=global_confirmed_cum.index,
            y=global_confirmed_cum.values,
            type='bar',
            title='Confirmed Cases',
            color='blue'
        ),
        html.H2(
            children='Recovered',
            style={
                'textAlign': 'right',
                'color': colors['text']
            }
        ),
        generate_plot(
            x=global_recovered_cum.index,
            y=global_recovered_cum.values,
            type='bar',
            title='Recovered',
            color='green'
        ),
        html.H2(
            children='Deaths',
            style={
                'textAlign': 'right',
                'color': colors['text']
            }
        ),
        generate_plot(
            x=global_deaths_cum.index,
            y=global_deaths_cum.values,
            type='bar',
            title='Deaths',
            color='red'
        ),
    ])


def render_global_new_content():
    """
        Render worldwide new cases stats
    """
    return html.Div(children=[
        html.H2(
            children='New Cases',
            style={
                'textAlign': 'right',
                'color': colors['text']
            }
        ),
        generate_plot(
            x=global_confirmed_new.index,
            y=global_confirmed_new.values,
            type='bar',
            title='New Cases',
            color='blue'
        ),
        html.H2(
            children='New Recovered',
            style={
                'textAlign': 'right',
                'color': colors['text']
            }
        ),
        generate_plot(
            x=global_new_recovered.index,
            y=global_new_recovered.values,
            type='bar',
            title='New Recovered',
            color='green'
        ),
        html.H2(
            children='New Deaths',
            style={
                'textAlign': 'right',
                'color': colors['text']
            }
        ),
        generate_plot(
            x=global_new_deaths.index,
            y=global_new_deaths.values,
            type='bar',
            title='New Deaths',
            color='red'
        ),
    ])


app.layout = serve_layout


@app.callback(
    Output('button-clicked', 'children'),
    [
        Input('cum_button', 'n_clicks_timestamp'),
        Input('new_cases_button', 'n_clicks_timestamp')
    ]
)
def display(btn1, btn2):
    if int(btn1) > int(btn2):
        return html.Div('Button "Cumulative Cases" was clicked!')
    else:
        return html.Div('Button "New cases" was clicked!')


@app.callback(
    Output('tabs-content', 'children'),
    [
        Input('tabs', 'value'),
        Input('cum_button', 'n_clicks_timestamp'),
        Input('new_cases_button', 'n_clicks_timestamp')
    ]
)
def render_content(tab, btn1, btn2):
    # Russia tab cumulative stats
    if tab == 'rus_tab' and (int(btn1) > int(btn2)):
        return render_rus_cumulative_content()
    # Russia tab new cases stats
    elif tab == 'rus_tab' and (int(btn1) < int(btn2)):
        return render_rus_new_content()
    # world tab cumulative stats
    elif tab == 'global_tab' and (int(btn1) > int(btn2)):
        return render_global_cumulative_content()
    # world tab new cases stats
    elif tab == 'global_tab' and (int(btn1) < int(btn2)):
        return render_global_new_content()


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port='8050')
