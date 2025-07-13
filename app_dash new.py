import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import math

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Constants
PROTEIN_GOAL = 120
MAX_PROTEIN = 120
DEFAULT_TIMER = 300

# All meal options, Proteinshake is last in list for ordering
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
            'background': 'conic-gradient(#10b981 0% 54.17%, #1e293b 54.17% 100%)',
            'margin': '0 auto', 'position': 'relative'
        }),
        html.Div(id='protein-text', style={'textAlign': 'center', 'fontSize': '2em', 'marginTop': '20px'}),
        dbc.Button("Gericht hinzufügen", color="success", id="add-meal-btn",
                   className="d-block mx-auto mt-4", style={'fontSize': '1.75em', 'padding': '0.75rem 2rem'}),
    ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center'}),

    dbc.Modal([
        dbc.ModalHeader("Gericht hinzufügen", close_button=True),
        dbc.ModalBody([
            dcc.Dropdown(
                id='meal-select',
                options=all_meals,  # Pass all options statically here
                placeholder="Gericht auswählen",
                style={'fontSize': '1.5em', 'marginBottom': '20px', 'color': 'black'},
                searchable=True,
                clearable=True
            ),
            dbc.Button("Hinzufügen", id="confirm-meal-btn", color="success", className="w-100", style={'fontSize': '1.5em'})
        ])
    ], id="meal-modal", is_open=False, centered=True, size="lg"),

    dbc.Modal([
        dbc.ModalHeader("Fast geschafft!", close_button=True),
        dbc.ModalBody([
            html.Div(id='timer-circle', style={
                'width': '150px', 'height': '150px', 'borderRadius': '50%',
                'background': 'conic-gradient(#10b981 0% 100%, #1e293b 100% 100%)',
                'margin': '20px auto', 'position': 'relative'
            }),
            html.P("Du hast noch 5 Minuten für das Tagesziel!", className="text-center", style={'fontSize': '1.2em'}),
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
        "position": "fixed", "bottom": "0", "left": "0", "width": "100%",
        "backgroundColor": "#1e293b", "padding": "0.5rem 0",
        "boxShadow": "0 -2px 5px rgba(0,0,0,0.3)", "zIndex": "1000"
    }),

    # Store to hold protein count
    dcc.Store(id="protein-store", data={"value": 65}),
    # Store to hold timer data
    dcc.Store(id="custom-timer", data={"total": DEFAULT_TIMER}),
], fluid=True, style={'backgroundColor': '#0a0f1f', 'color': '#f8fafc', 'minHeight': '100vh'})


@app.callback(
    [Output('protein-circle', 'style'),
     Output('protein-text', 'children'),
     Output('meal-modal', 'is_open'),
     Output('timer-modal', 'is_open'),
     Output('timer-interval', 'disabled'),
     Output('protein-store', 'data')],
    [Input('add-meal-btn', 'n_clicks'),
     Input('confirm-meal-btn', 'n_clicks')],
    [State('meal-select', 'value'),
     State('protein-store', 'data')]
)
def handle_meal(add_clicks, confirm_clicks, meal, store):
    protein = store.get("value", 0)
    trigger = dash.callback_context.triggered_id

    if trigger == 'add-meal-btn':
        return dash.no_update, f'{protein}/{PROTEIN_GOAL}g', True, False, True, store

    if trigger == 'confirm-meal-btn' and meal == 'Proteinshake':
        if protein < MAX_PROTEIN - 1:
            protein = min(MAX_PROTEIN, protein + 54)
        store = {"value": protein}

    progress = min(100, (protein / PROTEIN_GOAL) * 100)
    circle_style = {
        'width': '200px', 'height': '200px', 'borderRadius': '50%',
        'background': f'conic-gradient(#10b981 0% {progress}%, #1e293b {progress}% 100%)',
        'margin': '0 auto', 'position': 'relative'
    }

    show_modal = protein >= 119  # Trigger at 119 or more
    return circle_style, f'{protein}/{PROTEIN_GOAL}g', False, show_modal, not show_modal, store


@app.callback(
    [Output('timer-circle', 'style'),
     Output('timer-circle', 'children'),
     Output('custom-timer', 'data'),
     Output('timer-interval', 'disabled', allow_duplicate=True)],
    [Input('timer-interval', 'n_intervals'),
     Input('timer-input', 'value')],
    [State('custom-timer', 'data')],
    prevent_initial_call='initial_duplicate'
)
def update_timer(n, custom_time, timer_data):
    total_for_progress = DEFAULT_TIMER  # 300 seconds for the progress circle

    countdown_duration = custom_time if custom_time else timer_data.get("total", DEFAULT_TIMER)
    time_left = max(0, countdown_duration - n * 0.1)

    # Calculate percent relative to 300 seconds, not the countdown duration
    percent = (time_left / total_for_progress) * 100
    percent = max(0, min(100, percent))  # Clamp between 0 and 100 just in case

    style = {
        'width': '150px', 'height': '150px', 'borderRadius': '50%',
        'background': f'conic-gradient(#10b981 0% {percent}%, #1e293b {percent}% 100%)',
        'margin': '20px auto', 'position': 'relative'
    }

    time_text = html.Div(
        f'{math.floor(time_left / 60)}:{int(time_left % 60):02d}',
        style={'position': 'absolute', 'top': '50%', 'left': '50%',
               'transform': 'translate(-50%, -50%)', 'fontSize': '1.2em'}
    )

    return style, time_text, {"total": countdown_duration}, False if time_left > 0 else True


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8050)
