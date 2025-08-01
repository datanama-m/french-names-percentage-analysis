from dash import html, dcc
import dash_bootstrap_components as dbc


def create_header():
    return html.Div([
        html.H1("FRENCH FIRST NAMES DASHBOARD", className="display-4 text-center"),
        html.P("French Name Popularity by Percentage of Annual Births (1900-2021)",
               className="lead text-center"),
        html.P([
            "Data source: ",
            html.A("Insee", href="https://www.insee.fr/fr/statistiques/2540004#consulter", target="_blank"),
            " • Dashboard by ",
            html.A("Datanama", href="mailto:maxime@datanama.net", className="text-decoration-none")
        ], className="text-center small text-muted"),

        # Instructions section
        html.Div([
            html.H4("Instructions:", className="mb-2"),
            html.Ul([
                html.Li("Use the search box to find names (accent-sensitive)"),
                html.Li("Compare up to 5 names at once"),
                html.Li("Double-click on a name in the legend to isolate it"),
                html.Li("Drag on the graph to zoom into a time period"),
            ], className="list-group-flush ps-3 small"),
        ], className="bg-light p-3 rounded mt-3 shadow-sm mb-0")
    ], className="container my-4")


def create_controls(default_names):
    return html.Div([
        dcc.Store(id='previous-selection', data=[]),
        html.Div([
            html.Label("Gender", className="fw-bold"),
            dcc.RadioItems(
                id='gender-input',
                options=[{'label': g, 'value': g} for g in ['Male', 'Female']],
                value='Male',
                inline=True,
                className="mb-3",
                inputStyle={"margin-right": "10px"},
                labelStyle={"margin-right": "20px", "margin-bottom": "10px"}
            ),

            html.Label("Names", className="fw-bold"),
            dcc.Dropdown(
                id='name-input',
                multi=True,
                value=default_names,
                placeholder="Search names...",
                className="mb-3"
            ),

            html.Label("Year Range", className="fw-bold mt-3"),
            dcc.RangeSlider(
                id='year-range',
                min=1900, max=2021,
                value=[1900, 2021],
                marks={i: str(i) for i in range(1900, 2022, 20)},
                className="mt-2"
            )
        ], className="container")
    ], className="container my-4")
