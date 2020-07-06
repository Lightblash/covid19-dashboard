from dash.dependencies import Input, Output

from app import app


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
