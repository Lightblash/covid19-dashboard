import dash_core_components as dcc
import dash_html_components as html

import plotly.graph_objs as go
import plotly.express as px
import os
import pandas as pd

CONFIRMED_CSV = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'

RECOVERED_CSV = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'

DEATHS_CSV = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'

COUNTRIES_COORDINATES_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'country_centroids.csv')


def get_processed_df(metric_csv):
    """

        Parameter
        ---------

        metrics_csv : str
            Full url path to target csv file


        Return
        ------

        pandas.DataFrame
            Return processed pandas DataFrame
    """

    source_df = pd.read_csv(metric_csv)
    source_df.drop(columns=['Province/State'], inplace=True)
    source_df.rename(columns={'Country/Region': 'country'}, inplace=True)
    processed_df = source_df.drop(columns=['Lat', 'Long'])
    source_df = source_df[['country', 'Lat', 'Long']].drop_duplicates('country')
    processed_df = processed_df.melt(
        id_vars='country',
        var_name='date',
        value_name='value'
    )

    centroid_df = pd.read_csv(
        COUNTRIES_COORDINATES_CSV, usecols=['admin', 'Longitude', 'Latitude'])

    centroid_df.columns = ['country', 'Longitude', 'Latitude']
    processed_df['date'] = pd.to_datetime(processed_df['date'])
    processed_df = processed_df.groupby(['country', 'date']).value.sum().reset_index()
    processed_df['prev_value'] = processed_df.groupby('country').value.shift(1)
    processed_df['new_cases'] = processed_df.value - processed_df.prev_value
    processed_df.fillna(value={'new_cases': 0}, inplace=True)
    processed_df.drop(columns=['prev_value'], inplace=True)

    # join long and lat from centroid
    processed_df = processed_df.merge(centroid_df, how='left', on='country')

    # join long and lat for the
    processed_df = processed_df.merge(
        source_df,
        how='left',
        on='country'
    )

    processed_df['Lat'] = processed_df.apply(
        lambda x: x['Latitude'] if pd.notna(x['Latitude']) else x['Lat'], axis=1)
    processed_df['Long'] = processed_df.apply(
        lambda x: x['Longitude'] if pd.notna(x['Longitude']) else x['Long'], axis=1)

    processed_df.drop(columns=['Latitude', 'Longitude'], inplace=True)

    return processed_df


def get_metric_ser(df, metric_type, country=None):
    """
        Return specific metric from provided dataframe. If country
        is provided returns country specific stats.

        Parameter
        ---------

        df : pandas.DataFrame
            Processed DataFrame with function get_processed_df()

        metric_type : str
            One of ['cumulative', 'new']

        country : str
            If None global stats is provided

        Return
        ------

        pandas.Series
            Grouped by date cases
    """

    if not country:
        if metric_type == 'cumulative':
            return df.groupby('date').value.sum()
        if metric_type == 'new':
            return df.groupby('date').new_cases.sum()
    if country:
        if metric_type == 'cumulative':
            return df[df['country'] == country].groupby('date').value.sum()
        if metric_type == 'new':
            return df[df['country'] == country].groupby('date').new_cases.sum()


def generate_plot(x, y, type, title, color):
    """
        Generate dash core components graph object
    """
    return dcc.Graph(
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
                'plot_bgcolor': '#FFFFFF',
                'paper_bgcolor': '#FFFFFF',
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
                    # initial date range of xaxis
                    'range': ['2020-03-01', (x.max() + pd.DateOffset(days=1)).strftime('%Y-%m-%d')]
                },
                # 'autosize': False,
                # 'width': 600,
                # 'height': 500,
            }
        }
    )


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


def render_map_chart(confirmed_df):
    """
        Return map figure object
    """

    confirmed_df['Norm'] = (confirmed_df.value ** 0.5 / confirmed_df.value.max() ** 0.5) * 50

    confirmed_df.rename(columns={'value': 'Confirmed Cases'}, inplace=True)

    confirmed_df = confirmed_df.groupby([
        pd.Grouper(key='date', freq='2D'),
        'country',
        'Lat',
        'Long'
    ])['Confirmed Cases', 'Norm'].max().reset_index()

    confirmed_df['date'] = confirmed_df.date.astype(str)

    # call scatter_mapbox function from px. Note the attributes especially
    # normalisation of data and maximum marker size. The animation is done on Dates.
    fig_map = px.scatter_mapbox(
        confirmed_df,
        lat="Lat",
        lon="Long",
        color='Confirmed Cases',
        size='Norm',
        color_continuous_scale="Portland",
        size_max=50,
        animation_frame='date',
        center=dict({'lat': 32, 'lon': 4}),
        zoom=1,
        hover_data={
            'Norm': False,
            'country': True,
            'Confirmed Cases': ':,',
            'Lat': False,
            'Long': False,
        }
        # hover_name='Confirmed Cases'
        # title='Spread of the COVID-19 around the world. Confirmed cases'
    )
    # adjust layout
    fig_map.update_layout(
        mapbox_style="carto-positron",
        width=1250,
        height=630,
        margin={"r": 0, "t": 0, "l": 50, "b": 0}
    )
    # update frame speed
    fig_map.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 225
    # update different layouts
    fig_map.layout.sliders[0].currentvalue.xanchor = "left"
    fig_map.layout.sliders[0].currentvalue.offset = -100
    fig_map.layout.sliders[0].currentvalue.prefix = ""
    fig_map.layout.sliders[0].currentvalue.font.color = "indianred"
    fig_map.layout.sliders[0].currentvalue.font.size = 20
    # fig_map.layout.sliders[0].len = 1
    fig_map.layout.sliders[0].y = 1.1
    fig_map.layout.sliders[0].x = 0.1
    fig_map.layout.updatemenus[0].y = 1.27
    fig_map.layout.updatemenus[0].x = 0.08

    return fig_map


def render_rus_cumulative_content(rus_confirmed_cum_ser, rus_recovered_cum_ser,
                                  rus_deaths_cum_ser):
    """
        Render Russian cumulative stats
    """

    fig = get_key_metrics_fig(
        rus_confirmed_cum_ser, rus_recovered_cum_ser,
        rus_deaths_cum_ser, 'cumulative'
    )

    rus_active_cum_ser = rus_confirmed_cum_ser - rus_recovered_cum_ser

    return html.Div(children=[
        dcc.Graph(figure=fig),
        generate_plot(
            x=rus_confirmed_cum_ser.index,
            y=rus_confirmed_cum_ser.values,
            type='bar',
            title='Confirmed Cases',
            color='blue'
        ),
        generate_plot(
            x=rus_recovered_cum_ser.index,
            y=rus_recovered_cum_ser.values,
            type='bar',
            title='Recovered',
            color='green'
        ),
        generate_plot(
            x=rus_deaths_cum_ser.index,
            y=rus_deaths_cum_ser.values,
            type='bar',
            title='Deaths',
            color='red'
        ),
        generate_plot(
            x=rus_active_cum_ser.index,
            y=rus_active_cum_ser.values,
            type='bar',
            title='Active',
            color='orange'
        ),
    ])


def render_rus_new_content(rus_new_cases_ser, rus_new_recovered_ser,
                           rus_new_deaths_ser):
    """
        Render Russian new stats
    """

    fig = get_key_metrics_fig(
        rus_new_cases_ser, rus_new_recovered_ser, rus_new_deaths_ser, 'new'
    )

    rus_active_new_ser = rus_new_cases_ser - rus_new_recovered_ser

    return html.Div(children=[
        dcc.Graph(figure=fig),
        generate_plot(
            x=rus_new_cases_ser.index,
            y=rus_new_cases_ser.values,
            type='bar',
            title='New Cases',
            color='blue'
        ),
        generate_plot(
            x=rus_new_recovered_ser.index,
            y=rus_new_recovered_ser.values,
            type='bar',
            title='New Recovered',
            color='green'
        ),
        generate_plot(
            x=rus_new_deaths_ser.index,
            y=rus_new_deaths_ser.values,
            type='bar',
            title='New Deaths',
            color='red'
        ),
        generate_plot(
            x=rus_active_new_ser.index,
            y=rus_active_new_ser.values,
            type='bar',
            title='New active',
            color='orange',
        ),
    ])


def render_global_cumulative_content(
    global_confirmed_cum_ser, global_recovered_cum_ser,
    global_deaths_cum_ser, map_fig
):
    """
        Render worldwide cumulative stats
    """

    fig = get_key_metrics_fig(global_confirmed_cum_ser, global_recovered_cum_ser,
                              global_deaths_cum_ser, 'cumulative')

    global_active_cum_ser = global_confirmed_cum_ser - global_recovered_cum_ser

    return html.Div(children=[
        dcc.Graph(figure=fig),
        generate_plot(
            x=global_confirmed_cum_ser.index,
            y=global_confirmed_cum_ser.values,
            type='bar',
            title='Confirmed Cases',
            color='blue'
        ),
        generate_plot(
            x=global_recovered_cum_ser.index,
            y=global_recovered_cum_ser.values,
            type='bar',
            title='Recovered',
            color='green'
        ),
        generate_plot(
            x=global_deaths_cum_ser.index,
            y=global_deaths_cum_ser.values,
            type='bar',
            title='Deaths',
            color='red'
        ),
        generate_plot(
            x=global_active_cum_ser.index,
            y=global_active_cum_ser.values,
            type='bar',
            title='Active',
            color='orange'
        ),
        html.Div(
            'Spread of the COVID-19 around the world. Confirmed cases',
            style={
                # 'color': 'blue',
                'fontSize': 24,
                'marginBottom': 0,
                'paddingBottom': 0,
                'textAlign': 'center'
            }
        ),
        dcc.Graph(
            figure=map_fig
        )
    ])


def render_global_new_content(
    global_confirmed_new_ser, global_new_recovered_ser, global_new_deaths_ser
):
    """
        Render worldwide new cases stats
    """

    fig = get_key_metrics_fig(global_confirmed_new_ser, global_new_recovered_ser,
                              global_new_deaths_ser, 'new')

    global_active_new_ser = global_confirmed_new_ser - global_new_recovered_ser

    return html.Div(children=[
        dcc.Graph(figure=fig),
        generate_plot(
            x=global_confirmed_new_ser.index,
            y=global_confirmed_new_ser.values,
            type='bar',
            title='New Cases',
            color='blue'
        ),
        generate_plot(
            x=global_new_recovered_ser.index,
            y=global_new_recovered_ser.values,
            type='bar',
            title='New Recovered',
            color='green'
        ),
        generate_plot(
            x=global_new_deaths_ser.index,
            y=global_new_deaths_ser.values,
            type='bar',
            title='New Deaths',
            color='red'
        ),
        generate_plot(
            x=global_active_new_ser.index,
            y=global_active_new_ser.values,
            type='bar',
            title='New active',
            color='orange',
        ),
    ])


confirmed_df = get_processed_df(CONFIRMED_CSV)
recovered_df = get_processed_df(RECOVERED_CSV)
deaths_df = get_processed_df(DEATHS_CSV)

# confirmed
global_confirmed_cum = get_metric_ser(confirmed_df, 'cumulative')
global_confirmed_new = get_metric_ser(confirmed_df, 'new')
rus_confirmed_cum = get_metric_ser(confirmed_df, 'cumulative', 'Russia')
rus_new_cases = get_metric_ser(confirmed_df, 'new', 'Russia')

# recovered
global_recovered_cum = get_metric_ser(recovered_df, 'cumulative')
global_new_recovered = get_metric_ser(recovered_df, 'new')
rus_recovered_cum = get_metric_ser(recovered_df, 'cumulative', 'Russia')
rus_new_recovered = get_metric_ser(recovered_df, 'new', 'Russia')

# deaths
global_deaths_cum = get_metric_ser(deaths_df, 'cumulative')
global_new_deaths = get_metric_ser(deaths_df, 'new')
rus_deaths_cum = get_metric_ser(deaths_df, 'cumulative', 'Russia')
rus_new_deaths = get_metric_ser(deaths_df, 'new', 'Russia')

map_fig = render_map_chart(confirmed_df)

global_cum_layout = render_global_cumulative_content(
    global_confirmed_cum, global_recovered_cum, global_deaths_cum, map_fig
)
global_new_layout = render_global_new_content(
    global_confirmed_new, global_new_recovered, global_new_deaths
)
rus_cum_layout = render_rus_cumulative_content(
    rus_confirmed_cum, rus_recovered_cum, rus_deaths_cum
)
rus_new_layout = render_rus_new_content(
    rus_new_cases, rus_new_recovered, rus_new_deaths
)
