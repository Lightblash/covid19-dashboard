import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app, server
import layouts
import callbacks


app.layout = html.Div([
    # title of the dashboard
    html.H1('COVID-19 Dashboard'),
    # section with buttons
    html.Div([
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
    ], style={'textAlign': 'center'}
    ),
    html.Div(
        id='button-clicked',
        style={'textAlign': 'center', 'marginBottom': 10}
    ),
    # section with tabs
    dcc.Tabs(
        id="tabs", value='rus_tab',
        children=[
            dcc.Tab(label='Russia', value='rus_tab'),
            dcc.Tab(label='World', value='global_tab'),
        ]
    ),
    html.Div(id='tabs-content'),
])


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
        return layouts.rus_cum_layout
    # Russia tab new cases stats
    elif tab == 'rus_tab' and (int(btn1) < int(btn2)):
        return layouts.rus_new_layout
    # world tab cumulative stats
    elif tab == 'global_tab' and (int(btn1) > int(btn2)):
        return layouts.global_cum_layout
    # world tab new cases stats
    elif tab == 'global_tab' and (int(btn1) < int(btn2)):
        return layouts.global_new_layout


if __name__ == '__main__':
    app.run_server(debug=True)
