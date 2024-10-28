from dash import Dash, dcc,html,Output,Input
import dash_bootstrap_components as dbc
import numpy as np
import time
import board
import adafruit_scd4x


# start sensor collecting
i2c = board.I2C()
scd4x = adafruit_scd4x.SCD4X(i2c)
print("Serial number:", [hex(i) for i in scd4x.serial_number])

scd4x.start_periodic_measurement()
print("Waiting for first measurement....")


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

#app layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dcc.Markdown('# Mushroom App', style={'textAlign':'center',
                                                'color': 'mediumpurple'})
            ],width=12)
        ]),
    dbc.Row([
        dbc.Col([
            my_output := dcc.Markdown(children=''),
            my_text := dcc.Input(value="Type")
            ],width = 6),
        dbc.Col([
             dcc.Interval(
                id='interval-component',
                interval=6000,  # Update every interval/1000 second
                n_intervals=0),
             sensor_out := dcc.Markdown(children='')
            ],width=6)
        ])
    ])

#callback Interactivity
@app.callback(
    Output(my_output, component_property='children'),
    Input(my_text, component_property='value')
    )

def update_text(text):
    return text

@app.callback(
    Output(sensor_out, 'children'),
    Input('interval-component', 'n_intervals')
)
def update_output(n):
    #current_time = time.strftime("%H:%M:%S")
    sensor = "Waiting on sensor..."
    if scd4x.data_ready:
        print(f"CO2: {scd4x.CO2} ppm")
        print(f"Temperature: {(scd4x.temperature * 9 / 5) + 32:.0f} F")
        print(f"Humidity: {scd4x.relative_humidity:.1f}")
        print()
        sensor = f"Temp: {(scd4x.temperature * 9 / 5) + 32:.0f} F Humidity: {scd4x.relative_humidity:.1f} CO2: {scd4x.CO2} ppm"
    return sensor

#starting app
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)
