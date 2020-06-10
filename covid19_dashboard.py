# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

CONFIRMED_CSV = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'

RECOVERED_CSV = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'

DEATHS_CSV = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'


def get_metric_ser(metric_csv, metric_type, country=None):
    """

        Parameter
        ---------

        metrics_csv : str
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

# active
global_active_cum = global_confirmed_cum - global_recovered_cum
global_active_new = global_confirmed_new - global_new_recovered
rus_active_cum = rus_confirmed_cum - rus_recovered_cum
rus_active_new = rus_new_cases - rus_new_recovered

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

colors = {
    'background': '#FFFFFF',
    'text': '#8C9D95'
}


def serve_layout():
    """

    """
    return html.Div(
        [
            html.H1('COVID-19 Dashboard'),
            # section with buttons
            html.Div(
                [
                    html.Button(
                        'Cumulative', id='cum_button', n_clicks_timestamp=1,
                        className='btn active',
                        style={'backgroundColor': '#e7e7e7', 'color': 'black'}
                    ),
                    html.Button(
                        'New Cases', id='new_cases_button', n_clicks_timestamp=0,
                        className='btn',
                        style={'backgroundColor': '#e7e7e7', 'color': 'black'}
                    )
                ],
                style={'textAlign': 'center'}
            ),
            html.Div(
                id='button-clicked',
                style={'textAlign': 'center', 'marginBottom': 10}
            ),
            # section with tabs
            dcc.Tabs(id="tabs", value='rus_tab', children=[
                dcc.Tab(label='Russia', value='rus_tab'),
                dcc.Tab(label='World', value='global_tab'),
            ]),
            html.Div(id='tabs-content'),
        ]
    )


# determine which button is pressed
@app.callback(
    [Output('cum_button', 'style'),
     Output('new_cases_button', 'style')],
    [Input('cum_button', 'n_clicks_timestamp'),
     Input('new_cases_button', 'n_clicks_timestamp')]
)
def set_active_button_color(btn1, btn2):
    active = {'backgroundColor': '#008CBA', 'color': 'white'}
    passive = {'backgroundColor': '#e7e7e7', 'color': 'black'}
    if int(btn1) > int(btn2):
        return (active, passive)
    else:
        return (passive, active)


def generate_plot(x, y, type, title, color):
    """
        Generate dash core components graph object
    """
    return dcc.Graph(
        # id='articles_id',
        figure={
            'data': [
                {
                    'x': x,
                    'y': y,
                    'type': type,
                    'name': title,
                    'marker': {'color': color},
                }
            ],
            'layout': {
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'font': {'color': color},
                'color': color,
                'title': {
                    'text': title,
                    'font': {
                        'color': color,
                        'size': 24,
                    }
                },
                'xaxis': {
                    'range': ['2020-03-01', (x.max() + pd.DateOffset(days=1)).strftime('%Y-%m-%d')]
                },
                # 'autosize': False,
                # 'width': 600,
                # 'height': 500,
            }
        }
    )


def get_processed_df(metric_csv):
    """

        Parameter
        ---------

        metrics_csv : str
            Full url path to target csv file
    """

    df = pd.read_csv(metric_csv)
    df.drop(columns=['Province/State'], inplace=True)
    df = df.melt(
        id_vars=['Country/Region', 'Lat', 'Long'],
        var_name='date',
        value_name='value'
    )
    df['date'] = pd.to_datetime(df['date'])
    df = df.groupby(['Country/Region', 'date', 'Lat', 'Long']).value.sum().reset_index()
    df['prev_value'] = df.groupby('Country/Region').value.shift(1)
    df['new_cases'] = df.value - df.prev_value
    df.drop(columns=['prev_value'], inplace=True)

    return df


def render_map_chart():
    """

    """

    confirmed_df = get_processed_df(CONFIRMED_CSV)

    confirmed_df['date'] = confirmed_df.date.astype(str)

    norm = confirmed_df.groupby('date').value.max().reset_index()

    confirmed_df = confirmed_df.merge(norm, on='date', how='left')

    confirmed_df['Norm'] = confirmed_df.value_x / confirmed_df.value_y

    confirmed_df['Norm'].fillna(0, inplace=True)
    # call scatter_mapbox function from px. Note the attributes especially
    # normalisation of data and maximum maker size. The animation is done on Dates.
    fig_map = px.scatter_mapbox(
        confirmed_df, lat="Lat", lon="Long", color='value_x',
        size=confirmed_df['Norm'].round(3) ** 0.5 * 50,
        color_continuous_scale="thermal", size_max=50, animation_frame='date',
        center=dict({'lat': 32, 'lon': 4}), zoom=1, hover_data=['Country/Region']
    )
    # here on wards various layouts have been called in to bring it in the present shape
    fig_map.update_layout(

        mapbox_style="carto-positron",
        width=1250,
        height=630,
        margin={"r": 0, "t": 0, "l": 10, "b": 0}
    )
    # update frame speed
    fig_map.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 200
    # update different layouts
    fig_map.layout.sliders[0].currentvalue.xanchor = "left"
    fig_map.layout.sliders[0].currentvalue.offset = -100
    fig_map.layout.sliders[0].currentvalue.prefix = ""
    fig_map.layout.sliders[0].len = .9
    fig_map.layout.sliders[0].currentvalue.font.color = "indianred"
    fig_map.layout.sliders[0].currentvalue.font.size = 20
    fig_map.layout.sliders[0].y = 1.1
    fig_map.layout.sliders[0].x = 0.15
    fig_map.layout.updatemenus[0].y = 1.27

    return fig_map


map_fig = render_map_chart()


def get_key_metrics_fig(confirmed_ser, recovered_ser, deaths_ser, metric_type):
    """
        Return key metrics graph object figure

        Parameters

        ----------

        confirmed_ser: pandas.Series
            Confirmed pandas series objects with index=dates,
            values=number of cases

        recovered_ser: pandas.Series
            Recovered pandas series objects with index=dates,
            values=number of cases

        deaths_ser: pandas.Series
            Deaths pandas series objects with index=dates,
            values=number of cases

        metric_type: str
            One of ['cumulative', 'new]
    """

    fig = go.Figure()

    if metric_type == 'cumulative':
        mode = 'number+delta'
        delta_confirmed = {
            'reference': confirmed_ser.values[-2],
            'relative': False,
            'position': "bottom",
            'valueformat': ">,d",
            'increasing.color': 'blue',
            'increasing.symbol': '+'
        }

        delta_recovered = {
            'reference': recovered_ser.values[-2],
            'relative': False,
            'position': "bottom",
            'valueformat': ">,d",
            'increasing.color': 'green',
            'increasing.symbol': '+'
        }

        delta_deaths = {
            'reference': deaths_ser.values[-2],
            'relative': False,
            'position': "bottom",
            'valueformat': ">,d",
            'increasing.color': 'red',
            'increasing.symbol': '+'
        }

    elif metric_type == 'new':
        mode = 'number'
        delta_confirmed = None
        delta_recovered = None
        delta_deaths = None

    fig.add_trace(go.Indicator(
        mode=mode,
        value=confirmed_ser.values[-1],
        number={
            "valueformat": ">,d",
            'font': {
                'size': 60,
                'color': 'blue',
            }
        },
        domain={'row': 0, 'column': 0},
        title={
            'text': 'Confirmed',
            'font': {
                'size': 24,
                'color': 'blue',
            }
        },
        delta=delta_confirmed))

    fig.add_trace(go.Indicator(
        mode=mode,
        value=recovered_ser.values[-1],
        number={
            "valueformat": ">,d",
            'font': {
                'size': 60,
                'color': 'green',
            }
        },
        domain={'row': 0, 'column': 1},
        title={
            'text': 'Recovered',
            'font': {
                'size': 24,
                'color': 'green',
            }
        },
        delta=delta_recovered))

    fig.add_trace(go.Indicator(
        mode=mode,
        value=deaths_ser.values[-1],
        number={
            "valueformat": ">,d",
            'font': {
                'size': 60,
                'color': 'red',
            }
        },
        domain={'row': 0, 'column': 2},
        title={
            'text': 'Deaths',
            'font': {
                'size': 24,
                'color': 'red',
            }
        },
        delta=delta_deaths))

    fig.update_layout(
        grid={'rows': 1, 'columns': 3},
        autosize=True,
        # width=500,
        height=300,
        # margin={'t': 100, 'b': 100, 'l': 0, 'r': 0}
    )

    return fig


def render_rus_cumulative_content():
    """
        Render Russian cumulative stats
    """

    fig = get_key_metrics_fig(
        rus_confirmed_cum, rus_recovered_cum, rus_deaths_cum, 'cumulative'
    )

    return html.Div(children=[
        dcc.Graph(figure=fig),
        generate_plot(
            x=rus_confirmed_cum.index,
            y=rus_confirmed_cum.values,
            type='bar',
            title='Confirmed Cases',
            color='blue'
        ),
        generate_plot(
            x=rus_recovered_cum.index,
            y=rus_recovered_cum.values,
            type='bar',
            title='Recovered',
            color='green'
        ),
        generate_plot(
            x=rus_deaths_cum.index,
            y=rus_deaths_cum.values,
            type='bar',
            title='Deaths',
            color='red'
        ),
        generate_plot(
            x=rus_active_cum.index,
            y=rus_active_cum.values,
            type='bar',
            title='Active',
            color='orange'
        ),
    ])


def render_rus_new_content():
    """
        Render Russian new stats
    """

    fig = get_key_metrics_fig(
        rus_new_cases, rus_new_recovered, rus_new_deaths, 'new'
    )

    return html.Div(children=[
        dcc.Graph(figure=fig),
        generate_plot(
            x=rus_new_cases.index,
            y=rus_new_cases.values,
            type='bar',
            title='New Cases',
            color='blue'
        ),
        generate_plot(
            x=rus_new_recovered.index,
            y=rus_new_recovered.values,
            type='bar',
            title='New Recovered',
            color='green'
        ),
        generate_plot(
            x=rus_new_deaths.index,
            y=rus_new_deaths.values,
            type='bar',
            title='New Deaths',
            color='red'
        ),
        generate_plot(
            x=rus_active_new.index,
            y=rus_active_new.values,
            type='bar',
            title='New active',
            color='orange',
        ),
    ])


def render_global_cumulative_content():
    """
        Render worldwide cumulative stats
    """

    fig = get_key_metrics_fig(global_confirmed_cum, global_recovered_cum,
                              global_deaths_cum, 'cumulative')

    return html.Div(children=[
        dcc.Graph(figure=fig),
        generate_plot(
            x=global_confirmed_cum.index,
            y=global_confirmed_cum.values,
            type='bar',
            title='Confirmed Cases',
            color='blue'
        ),
        generate_plot(
            x=global_recovered_cum.index,
            y=global_recovered_cum.values,
            type='bar',
            title='Recovered',
            color='green'
        ),
        generate_plot(
            x=global_deaths_cum.index,
            y=global_deaths_cum.values,
            type='bar',
            title='Deaths',
            color='red'
        ),
        generate_plot(
            x=global_active_cum.index,
            y=global_active_cum.values,
            type='bar',
            title='Active',
            color='orange'
        ),
        dcc.Graph(
            figure=map_fig
        )
    ])


def render_global_new_content():
    """
        Render worldwide new cases stats
    """

    fig = get_key_metrics_fig(global_confirmed_new, global_new_recovered,
                              global_new_deaths, 'new')

    return html.Div(children=[
        dcc.Graph(figure=fig),
        generate_plot(
            x=global_confirmed_new.index,
            y=global_confirmed_new.values,
            type='bar',
            title='New Cases',
            color='blue'
        ),
        generate_plot(
            x=global_new_recovered.index,
            y=global_new_recovered.values,
            type='bar',
            title='New Recovered',
            color='green'
        ),
        generate_plot(
            x=global_new_deaths.index,
            y=global_new_deaths.values,
            type='bar',
            title='New Deaths',
            color='red'
        ),
        generate_plot(
            x=global_active_new.index,
            y=global_active_new.values,
            type='bar',
            title='New active',
            color='orange',
        ),
    ])


app.layout = serve_layout


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
