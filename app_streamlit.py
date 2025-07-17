
import dash
from dash import html, dcc, Input, Output, State, callback_context, clientside_callback
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
        Output('timer-start-timestamp', 'data')
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
                'top': '50%',
                'left': '50%',
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
        return style, children, True, True, dash.no_update

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
    return style, children, False, not enable_delay, time.time() if enable_delay else dash.no_update

@app.callback(
    [
        Output('timer-modal', 'is_open'),
        Output('modal-delay-interval', 'disabled', allow_duplicate=True),
        Output('modal-delay-interval', 'n_intervals'),
        Output('custom-timer', 'data')
    ],
    [Input('modal-delay-interval', 'n_intervals')],
    [State('timer-modal', 'is_open'),
     State('timer-input', 'value')],
    prevent_initial_call='initial_duplicate'
)
def open_timer_modal(n_intervals, is_open, timer_input):
    if n_intervals > 0 and not is_open:
        # Set the timer duration when the modal opens
        timer_data = {"total": timer_input if timer_input is not None else DEFAULT_TIMER}
        return True, True, 0, timer_data
    return is_open, True, 0, dash.no_update

# Client-side callback for timer
clientside_callback(
    f"""
    function(timer_modal_is_open, timer_data, timer_input, start_timestamp) {{
        if (!timer_modal_is_open || !timer_data || !timer_data.total) {{
            return [
                {{'display': 'none'}},  // Hide timer-circle
                null,                   // No children
                timer_data,             // Preserve timer_data
                start_timestamp         // Preserve start_timestamp
            ];
        }}

        const now = Date.now() / 1000;  // Current time in seconds
        const total_duration = {DEFAULT_TIMER};      // DEFAULT_TIMER
        let time_left = timer_data.total - (now - start_timestamp);

        if (time_left <= 0) {{
            time_left = 0;
            clearInterval(window.timerInterval);  // Stop the interval
        }}

        const percent = Math.max(0, Math.min(100, (time_left / total_duration) * 100));
        let color;
        if (time_left > total_duration * 2 / 3) {{
            color = '#10b981';  // Green
        }} else if (time_left > total_duration * 1 / 3) {{
            color = '#eab308';  // Yellow
        }} else {{
            color = '#ef4444';  // Red
        }}

        const style = {{
            width: '150px',
            height: '150px',
            borderRadius: '50%',
            background: `conic-gradient(${{color}} 0% ${{percent}}%, #1e293b ${{percent}}% 100%)`,
            margin: '20px auto',
            position: 'relative'
        }};

        const minutes = Math.floor(time_left / 60);
        const seconds = Math.floor(time_left % 60);
        const time_text = [
            {{
                type: 'div',
                props: {{
                    style: {{
                        position: 'absolute',
                        top: '50%',
                        left: '50%',
                        transform: 'translate(-50%, -50%)',
                        width: '110px',
                        height: '110px',
                        borderRadius: '50%',
                        backgroundColor: '#0a0f1f'
                    }}
                }},
            }},
            {{
                type: 'div',
                props: {{
                    children: `${{minutes}}:${{seconds.toString().padStart(2, '0')}}`,
                    style: {{
                        position: 'absolute',
                        top: '50%',
                        left: '50%',
                        transform: 'translate(-50%, -50%)',
                        fontSize: '1.2em',
                        color: '#f8fafc'
                    }}
                }}
            }}
        ];

        return [style, time_text, timer_data, start_timestamp];
    }}
    """,
    [
        Output('timer-circle', 'style'),
        Output('timer-circle', 'children'),
        Output('custom-timer', 'data'),
        Output('timer-start-timestamp', 'data', allow_duplicate=True)
    ],
    [
        Input('timer-modal', 'is_open'),
        State('custom-timer', 'data'),
        State('timer-input', 'value'),
        State('timer-start-timestamp', 'data')
    ],
    prevent_initial_call=True
)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050)
