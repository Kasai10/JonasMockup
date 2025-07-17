import dash
from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import math
import time
import uuid

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Constants
PROTEIN_GOAL = 120
MAX_PROTEIN = 119
DEFAULT_TIMER = 300  # in seconds

all_meals = sorted([
    {'label': 'Hähnchenbrust', 'value': 'ChickenBreast'},
    {'label': 'Lachsfilet', 'value': 'SalmonFilet'},
    {'label': 'Quark', 'value': 'Quark'},
    {'label': 'Rindfleisch ', 'value': 'Beef'},
    {'label': 'Tofu', 'value': 'Tofu'},
    {'label': 'Eier', 'value': 'Eggs'}
], key=lambda x: x['label']) + [{'label': 'Proteinshake', 'value': 'Proteinshake'}]

app.layout = dbc.Container([
    html.H1("MyPump", className="text-center mt-5 mb-4", style={'fontSize': '4em', 'fontWeight': 'bold'}),
    html.H3("Dein Proteinziel heute:", className="text-center mb-5", style={'fontSize': '2.5em'}),

    html.Div([
        html.Div(id='protein-circle', style={
            'width': '250px', 'height': '250px', 'borderRadius': '50%',
            'background': 'conic-gradient(#eab308 0% 54.17%, #1e293b 54.17% 100%)',
            'margin': '0 auto', 'position': 'relative'
        }),
        dbc.Button("Gericht hinzufügen", color="success", id="add-meal-btn",
                   className="d-block mx-auto mt-4", style={'fontSize': '1.75em', 'padding': '0.75rem 2rem'}),
    ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center'}),

    dbc.Modal([
        dbc.ModalHeader("Gericht hinzufügen", close_button=True),
        dbc.ModalBody([
            dcc.Dropdown(
                id='meal-select',
                options=all_meals,
                placeholder="Gericht auswählen",
                style={'fontSize': '1.5em', 'marginBottom': '20px', 'color': 'black'},
                searchable=True,
                clearable=True
            ),
            dbc.Button("Hinzufügen", id="confirm-meal-btn", color="success", className="w-100", style={'fontSize': '1.5em'})
        ])
    ], id="meal-modal", is_open=False, centered=True, size="lg"),

    dbc.Modal([
        dbc.ModalHeader(
            "Fast geschafft!",
            close_button=True,
            style={'textAlign': 'center', 'fontWeight': 'bold', 'fontSize': '1.5em', 'width': '100%'}
        ),
        dbc.ModalBody([
            html.Div(id='timer-circle', style={
                'width': '150px', 'height': '150px', 'borderRadius': '50%',
                'background': 'conic-gradient(#10b981 0% 100%, #1e293b 100% 100%)',
                'margin': '20px auto', 'position': 'relative'
            }),
            html.P(
                "Du hast noch 5 Minuten für dein Tagesziel!",
                className="text-center",
                style={'fontSize': '1.75em', 'fontWeight': 'bold'}
            ),
            dcc.Interval(id='timer-interval', interval=100, n_intervals=0, disabled=True)
        ])
    ], id="timer-modal", is_open=False, centered=True, size="lg"),

    html.Div([
        html.H5("🛠 Timer anpassen", style={'textAlign': 'center'}),
        dcc.Input(
            id='timer-input',
            type='number',
            value=DEFAULT_TIMER,
            placeholder='Zeit in Sekunden',
            min=10, max=1800,
            style={'width': '200px', 'margin': '0 auto', 'display': 'block', 'textAlign': 'center'}
        )
    ], style={'marginTop': '100vh', 'paddingBottom': '200px'}),

    html.Div([
        dbc.Nav([
            dbc.NavLink([html.I(className="fas fa-utensils me-2"), "Essen"], href="#", active=True),
            dbc.NavLink([html.I(className="fas fa-dumbbell me-2"), "Gewichte"], href="#"),
            dbc.NavLink([html.I(className="fas fa-user me-2"), "Profil"], href="#"),
        ], pills=True, justified=True)
    ], style={
        'position': 'fixed', 'bottom': '0', 'left': '0', 'width': '100%',
        'backgroundColor': '#1e293b', 'padding': '0.5rem 0',
        'boxShadow': '0 -2px 5px rgba(0,0,0,0.3)', 'zIndex': '1000'
    }),

    dcc.Store(id="protein-store", data={"value": 65}),
    dcc.Store(id="custom-timer", data={"total": DEFAULT_TIMER}),
    dcc.Store(id="timer-start-timestamp", data=None),  # Store when timer started
    dcc.Interval(id='modal-delay-interval', interval=3000, n_intervals=0, disabled=True)  # 3-second delay for modal
], fluid=True, style={'backgroundColor': '#0a0f1f', 'color': '#f8fafc', 'minHeight': '100vh', 'width': '100vw', 'margin': '0', 'padding': '0'})

@app.callback(
    [
        Output('protein-circle', 'style'),
        Output('protein-circle', 'children'),
        Output('meal-modal', 'is_open'),
        Output('modal-delay-interval', 'disabled'),
        Output('timer-interval', 'disabled'),
        Output('protein-store', 'data')
    ],
    [Input('add-meal-btn', 'n_clicks'),
     Input('confirm-meal-btn', 'n_clicks')],
    [State('meal-select', 'value'),
     State('protein-store', 'data')]
)
def handle_meal(add_clicks, confirm_clicks, meal, store):
    protein = store.get("value", 0)
    trigger = callback_context.triggered_id

    if trigger == 'add-meal-btn':
        progress = min(100, (protein / PROTEIN_GOAL) * 100)
        color = "#eab308" if protein < 119 else "#10b981"
        style = {
            'width': '200px', 'height': '200px', 'borderRadius': '50%',
            'background': f'conic-gradient({color} 0% {progress}%, #1e293b {progress}% 100%)',
            'margin': '0 auto', 'position': 'relative'
        }
        children = html.Div([
            html.Div(style={
                'position': 'absolute',
                'top': '50%', 'left': '50%',
                'transform': 'translate(-50%, -50%)',
                'width': '110px', 'height': '110px',
                'borderRadius': '50%',
                'backgroundColor': '#0a0f1f',
            }),
            html.Div(f'{protein}/{PROTEIN_GOAL}g', style={
                'position': 'absolute',
                'top': '50%', 'left': '50%',
                'transform': 'translate(-50%, -50%)',
                'fontSize': '1.5em', 'color': '#f8fafc'
            })
        ])
        return style, children, True, True, True, store

    if trigger == 'confirm-meal-btn' and meal:
        # Add protein amount per meal, hardcoded example
        meal_protein_map = {
            'Proteinshake': 54,
            'ChickenBreast': 30,
            'SalmonFilet': 25,
            'Quark': 20,
            'Beef': 40,
            'Tofu': 15,
            'Eggs': 12
        }
        add_protein = meal_protein_map.get(meal, 0)
        if protein < MAX_PROTEIN:
            protein = min(MAX_PROTEIN, protein + add_protein)
        store = {"value": protein}

    progress = min(100, (protein / PROTEIN_GOAL) * 100)
    color = "#eab308" if protein < 119 else "#10b981"
    style = {
        'width': '200px', 'height': '200px', 'borderRadius': '50%',
        'background': f'conic-gradient({color} 0% {progress}%, #1e293b {progress}% 100%)',
        'margin': '0 auto', 'position': 'relative'
    }
    children = html.Div([
        html.Div(style={
            'position': 'absolute',
            'top': '50%', 'left': '50%',
            'transform': 'translate(-50%, -50%)',
            'width': '110px', 'height': '110px',
            'borderRadius': '50%',
            'backgroundColor': '#0a0f1f'
        }),
        html.Div(f'{protein}/{PROTEIN_GOAL}g', style={
            'position': 'absolute',
            'top': '50%', 'left': '50%',
            'transform': 'translate(-50%, -50%)',
            'fontSize': '1.5em', 'color': '#f8fafc'
        })
    ])

    enable_delay = protein >= 119
    return style, children, False, not enable_delay, True, store  # Keep timer disabled until modal opens


@app.callback(
    [
        Output('timer-modal', 'is_open'),
        Output('modal-delay-interval', 'disabled', allow_duplicate=True),
        Output('modal-delay-interval', 'n_intervals'),
        Output('timer-interval', 'disabled', allow_duplicate=True),
        Output('timer-start-timestamp', 'data', allow_duplicate=True)
    ],
    [Input('modal-delay-interval', 'n_intervals')],
    [State('timer-modal', 'is_open')],
    prevent_initial_call='initial_duplicate'
)
def open_timer_modal(n_intervals, is_open):
    if n_intervals > 0 and not is_open:
        # Start the timer when the modal opens by enabling timer-interval and setting start timestamp
        return True, True, 0, False, time.time()  # Open modal, disable delay interval, reset n_intervals, enable timer, set start time
    return is_open, True, 0, True, None  # Keep modal state, ensure delay interval is disabled, keep timer disabled


@app.callback(
    [
        Output('timer-circle', 'style'),
        Output('timer-circle', 'children'),
        Output('custom-timer', 'data'),
        Output('timer-interval', 'disabled', allow_duplicate=True),
        Output('timer-start-timestamp', 'data', allow_duplicate=True),
    ],
    [
        Input('timer-interval', 'n_intervals'),
        Input('timer-input', 'value'),
    ],
    [
        State('custom-timer', 'data'),
        State('timer-start-timestamp', 'data')
    ],
    prevent_initial_call='initial_duplicate'
)
def update_timer(n_intervals, input_time, timer_data, start_timestamp):
    # Use current time for syncing timer
    now = time.time()

    # Always use DEFAULT_TIMER for total duration to keep color logic consistent
    total_duration = DEFAULT_TIMER

    # Initialize timer data if not set
    if timer_data is None:
        timer_data = {"total": DEFAULT_TIMER}

    # If there's no start timestamp or input time has changed significantly
    if start_timestamp is None or (input_time and abs(timer_data.get("total", DEFAULT_TIMER) - input_time) > 1):
        # Use input time or default for total duration
        timer_data = {"total": input_time if input_time is not None else DEFAULT_TIMER}
        # If timer is running (start_timestamp is None means timer hasn't started), don't reset start time
        start_timestamp = start_timestamp or now

    # Calculate elapsed time since start
    elapsed = now - start_timestamp if start_timestamp else 0

    # Calculate time left
    time_left = max(0, timer_data.get("total", DEFAULT_TIMER) - elapsed)

    # Calculate progress percentage
    percent = (time_left / total_duration) * 100 if total_duration else 0
    percent = max(0, min(100, percent))

    # Color logic: green > yellow > red
    if time_left > total_duration * 2 / 3:
        color = "#10b981"  # Green
    elif time_left > total_duration * 1 / 3:
        color = "#eab308"  # Yellow
    else:
        color = "#ef4444"  # Red

    style = {
        'width': '150px', 'height': '150px', 'borderRadius': '50%',
        'background': f'conic-gradient({color} 0% {percent}%, #1e293b {percent}% 100%)',
        'margin': '20px auto', 'position': 'relative'
    }

    time_text = html.Div([
        html.Div(style={
            'position': 'absolute',
            'top': '50%', 'left': '50%',
            'transform': 'translate(-50%, -50%)',
            'width': '110px', 'height': '110px',
            'borderRadius': '50%',
            'backgroundColor': '#0a0f1f'
        }),
        html.Div(
            f'{math.floor(time_left / 60)}:{int(time_left % 60):02d}',
            style={
                'position': 'absolute',
                'top': '50%', 'left': '50%',
                'transform': 'translate(-50%, -50%)',
                'fontSize': '1.2em', 'color': '#f8fafc'
            }
        )
    ])

    timer_finished = time_left <= 0

    return style, time_text, timer_data, timer_finished, start_timestamp


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050)