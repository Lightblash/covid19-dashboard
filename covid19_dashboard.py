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

server = app.server

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
                    html.Button('Cumulative', id='cum_button', n_clicks_timestamp=1, className='btn active'),
                    html.Button('New Cases', id='new_cases_button', n_clicks_timestamp=0, className='btn')
                ],
                style={'textAlign': 'center'}
            ),
            html.Div(
                id='button-clicked',
                style={'textAlign': 'center', 'marginBottom': 10}
            ),
            dcc.Tabs(id="tabs", value='rus_tab', children=[
                dcc.Tab(label='Russia', value='rus_tab'),
                dcc.Tab(label='World', value='global_tab'),
            ]),
            html.Div(id='tabs-content'),
        ]
    )


@app.callback(
    [Output('cum_button', 'className'),
     Output('new_cases_button', 'className')],
    [Input('cum_button', 'n_clicks_timestamp'),
     Input('new_cases_button', 'n_clicks_timestamp')]
)
def set_active_button(btn1, btn2):
    if int(btn1) > int(btn2):
        return ('btn active', 'btn')
    else:
        return ('btn', 'btn active')


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
        number={
            "valueformat": ">,d",
            'font': {
                'size': 60,
                'color': 'blue'
            }
        },
        domain={'row': 0, 'column': 0},
        # domain={'x': [0, 0.4], 'y': [0, 1]},
        title={
            'text': 'Confirmed',
            'font': {
                'size': 24,
            }
        },
        delta={
            'reference': rus_confirmed_cum.values[-2],
            'relative': False,
            'position': "bottom",
            'valueformat': ">,d",
            'increasing.color': 'blue',
            'increasing.symbol': '+',
        }))

    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=rus_recovered_cum.values[-1],
        number={
            "valueformat": ">,d",
            'font': {
                'size': 60,
                'color': 'green'
            }
        },
        domain={'row': 0, 'column': 1},
        # domain={'x': [0.4, 0.8], 'y': [0, 1]},
        title={
            'text': 'Recovered',
            'font': {
                'size': 24,
            }
        },
        delta={
            'reference': rus_recovered_cum.values[-2],
            'relative': False,
            'position': "bottom",
            'valueformat': ">,d",
            'increasing.color': 'green',
            'increasing.symbol': '+'
        }))

    fig.add_trace(go.Indicator(
        mode="number+delta",
        align='center',
        value=rus_deaths_cum.values[-1],
        number={
            "valueformat": ">,d",
            'font': {
                'size': 60,
                'color': 'red',
            }
        },
        domain={'row': 0, 'column': 2},
        # domain={'x': [0.8, 1], 'y': [0, 1]},
        title={
            'text': 'Deaths',
            'font': {
                'size': 24,
            }
        },
        delta={
            'reference': rus_deaths_cum.values[-2],
            'relative': False,
            'position': "bottom",
            'valueformat': ">,d",
            'increasing.color': 'red',
            'increasing.symbol': '+',
            # 'font.size': 48
        }))

    fig.update_layout(
        grid={'rows': 1, 'columns': 3},
        autosize=True,
        # width=500,
        height=300
    )

    return html.Div(children=[
        dcc.Graph(figure=fig),
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

    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode="number",
        align='center',
        value=rus_new_cases.values[-1],
        number={
            "valueformat": ">,d",
            'font': {
                'color': 'blue',
                'size': 60,
            }
        },
        domain={'row': 0, 'column': 0},
        title={
            'text': 'New Cases',
            'font': {
                'color': 'blue',
                'size': 24,
            }
        },
    ))

    fig.add_trace(go.Indicator(
        mode="number",
        align='center',
        value=rus_new_recovered.values[-1],
        number={
            "valueformat": ">,d",
            'font': {
                'color': 'green',
                'size': 60,
            }
        },
        domain={'row': 0, 'column': 1},
        title={
            'text': 'New Recovered',
            'font': {
                'color': 'green',
                'size': 24,
            }
        },
    ))

    fig.add_trace(go.Indicator(
        mode="number",
        align='center',
        value=rus_new_deaths.values[-1],
        number={
            "valueformat": ">,d",
            'font': {
                'color': 'red',
                'size': 60,
            }
        },
        domain={'row': 0, 'column': 2},
        title={
            'text': 'New Deaths',
            'font': {
                'color': 'red',
                'size': 24,
            }
        },
    ))

    fig.update_layout(
        grid={'rows': 1, 'columns': 3},
        autosize=True,
        # width=500,
        height=250
    )

    return html.Div(children=[
        dcc.Graph(figure=fig),
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
        align='center',
        value=global_confirmed_cum.values[-1],
        number={
            "valueformat": ">,d",
            'font': {
                'color': 'blue',
                'size': 60,
            }
        },
        domain={'row': 0, 'column': 0},
        title={
            'text': 'Confirmed',
            'font': {
                'color': 'blue',
                'size': 24,
            }
        },
        delta={
            'reference': global_confirmed_cum.values[-2],
            'relative': False,
            'position': "bottom",
            'valueformat': ">,d",
            'increasing.color': 'blue',
            'increasing.symbol': '+',
        }))

    fig.add_trace(go.Indicator(
        mode="number+delta",
        align='center',
        value=global_recovered_cum.values[-1],
        number={
            "valueformat": ">,d",
            'font': {
                'color': 'green',
                'size': 60,
            }
        },
        domain={'row': 0, 'column': 1},
        title={
            'text': 'Recovered',
            'font': {
                'color': 'green',
                'size': 24,
            }
        },
        delta={
            'reference': global_recovered_cum.values[-2],
            'relative': False,
            'position': "bottom",
            'valueformat': ">,d",
            'increasing.color': 'green',
            'increasing.symbol': '+'
        }))

    fig.add_trace(go.Indicator(
        mode="number+delta",
        align='center',
        value=global_deaths_cum.values[-1],
        number={
            "valueformat": ">,d",
            'font': {
                'color': 'red',
                'size': 60,
            }
        },
        domain={'row': 0, 'column': 2},
        title={
            'text': 'Deaths',
            'font': {
                'color': 'red',
                'size': 24,
            }
        },
        delta={
            'reference': global_deaths_cum.values[-2],
            'relative': False,
            'position': "bottom",
            'valueformat': ">,d",
            'increasing.color': 'red',
            'increasing.symbol': '+'
        }))

    fig.update_layout(
        grid={'rows': 1, 'columns': 3},
        autosize=True,
        # width=500,
        height=300
    )

    return html.Div(children=[
        dcc.Graph(figure=fig),
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

    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode="number",
        align='center',
        value=global_confirmed_new.values[-1],
        number={
            "valueformat": ">,d",
            'font': {
                'color': 'blue',
                'size': 60,
            }
        },
        domain={'row': 0, 'column': 0},
        title={
            'text': 'New Cases',
            'font': {
                'color': 'blue',
                'size': 24,
            }
        },
    ))

    fig.add_trace(go.Indicator(
        mode="number",
        align='center',
        value=global_new_recovered.values[-1],
        number={
            "valueformat": ">,d",
            'font': {
                'color': 'green',
                'size': 60,
            }
        },
        domain={'row': 0, 'column': 1},
        title={
            'text': 'New Recovered',
            'font': {
                'color': 'green',
                'size': 24,
            }
        },
    ))

    fig.add_trace(go.Indicator(
        mode="number",
        align='center',
        value=global_new_deaths.values[-1],
        number={
            "valueformat": ">,d",
            'font': {
                'color': 'red',
                'size': 60,
            }
        },
        domain={'row': 0, 'column': 2},
        title={
            'text': 'New Deaths',
            'font': {
                'color': 'red',
                'size': 24,
            }
        },
    ))

    fig.update_layout(
        grid={'rows': 1, 'columns': 3},
        autosize=True,
        # width=500,
        height=250
    )

    return html.Div(children=[
        dcc.Graph(figure=fig),
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


# @app.callback(
#     Output('button-clicked', 'children'),
#     [
#         Input('cum_button', 'n_clicks_timestamp'),
#         Input('new_cases_button', 'n_clicks_timestamp')
#     ]
# )
# def display(btn1, btn2):
#     if int(btn1) > int(btn2):
#         return html.Div('Button "Cumulative Cases" was clicked!')
#     else:
#         return html.Div('Button "New cases" was clicked!')


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
    app.run_server(debug=True)
