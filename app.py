import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
from typing import List
from src.data_processing import get_processed_data
from src.components import create_header, create_controls

DATA_FILE = 'data/nat2021.csv'
DEFAULT_NAMES = ['PHILIPPE', 'GÉRALD', 'GREGORY', 'ZIDANE']


class NamesDashboard:
    def __init__(self):
        self.df_agg = get_processed_data(DATA_FILE)
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
        self.setup_layout()
        self.setup_callbacks()

    def setup_layout(self):
        self.app.layout = dbc.Container([
            create_header(),
            create_controls(DEFAULT_NAMES),
            html.Div(id='year-range-display', className="text-center fw-bold mb-3"),
            dcc.Graph(id='name-graph'),
            html.Div(id='stats-container'),
            dbc.Button("Download Data", id='btn-download', className="mt-3"),
            dcc.Download(id="download-data")
        ], fluid=True)

    def setup_callbacks(self):
        @self.app.callback(
            Output('name-input', 'options'),
            Input('gender-input', 'value')
        )
        def update_name_options(gender):
            names = sorted(self.df_agg[self.df_agg.Gender == gender]['Name'].unique())
            return [{'label': name, 'value': name} for name in names]

        @self.app.callback(
            Output('year-range-display', 'children'),
            Input('year-range', 'value')
        )
        def display_year_range(years):
            return f"Selected years: {years[0]} - {years[1]}"

        @self.app.callback(
            [Output('name-graph', 'figure'), Output('stats-container', 'children')],
            [Input('gender-input', 'value'), Input('name-input', 'value'), Input('year-range', 'value')]
        )
        def update_graph(gender, selected_names, year_range):
            filtered_df = self.df_agg[
                (self.df_agg.Gender == gender) &
                (self.df_agg.Name.isin(selected_names)) &
                (self.df_agg.Year.between(year_range[0], year_range[1]))
                ]

            fig = px.line(
                filtered_df,
                x='Year',
                y='Percentage',
                color='Name',
                title=f'Name Popularity Trends ({gender})',
                custom_data=['Name', 'Year', 'Percentage', 'Count', 'Total_Count']
            )

            fig.update_xaxes(tickformat="d")
            fig.update_traces(
                hovertemplate=(
                        "%{customdata[0]}<br>" +
                        "Year: %{customdata[1]}<br>" +
                        "Percentage: %{customdata[2]:.3f}%<br>" +
                        "Total (name): %{customdata[3]:,}<br>" +
                        "Total (gender): %{customdata[4]:,}<extra></extra>"
                )
            )

            stats_cards = self.generate_stats_cards(filtered_df, selected_names)
            return fig, stats_cards

        @self.app.callback(
            Output("download-data", "data"),
            Input("btn-download", "n_clicks"),
            [State('gender-input', 'value'), State('name-input', 'value'), State('year-range', 'value')],
            prevent_initial_call=True
        )
        def download_data(n_clicks, gender, selected_names, year_range):
            _ = n_clicks  # Silence unused parameter warning

            mask = (
                    (self.df_agg.Gender == gender) &
                    (self.df_agg.Name.isin(selected_names)) &
                    (self.df_agg.Year.between(year_range[0], year_range[1]))
            )

            download_df = self.df_agg[mask]
            return dcc.send_data_frame(
                download_df.to_csv, "name_trends.csv", index=False
            )

    def generate_stats_cards(self, df: pd.DataFrame, selected_names: List[str]) -> html.Div:
        """Generate statistics cards for selected names."""
        stats_cards = []

        for name in selected_names:
            name_data = df[df['Name'] == name]
            if not name_data.empty:
                peak_row = name_data.loc[name_data['Percentage'].idxmax()]
                first_row = name_data.loc[name_data['Year'].idxmin()]
                latest_row = name_data.loc[name_data['Year'].idxmax()]

                card = dbc.Card([
                    dbc.CardHeader(html.H3(name, className="text-center")),
                    dbc.CardBody([
                        html.P([
                            html.Span("Peak Year: ", className="fw-bold"),
                            f"{int(peak_row['Year'])} ({peak_row['Percentage']:.3f}%)"
                        ], className="mb-2"),
                        html.P([
                            html.Span("First Year: ", className="fw-bold"),
                            f"{int(first_row['Year'])} ({first_row['Percentage']:.3f}%)"
                        ], className="mb-2"),
                        html.P([
                            html.Span("Latest Year: ", className="fw-bold"),
                            f"{int(latest_row['Year'])} ({latest_row['Percentage']:.3f}%)"
                        ], className="mb-2"),
                        html.P([
                            html.Span("Total Births: ", className="fw-bold"),
                            f"{name_data['Count'].sum():,}"
                        ], className="mb-2"),
                    ])
                ], className="mb-3 shadow-sm")
                stats_cards.append(card)

        # Return html.Div containing the Row (fixes the type error)
        return html.Div([
            dbc.Row([
                dbc.Col(card, width=12, md=6, lg=4, className="mb-4")
                for card in stats_cards
            ])
        ])

    def run_server(self, **kwargs):
        """Run the Dash server."""
        self.app.run_server(**kwargs)


if __name__ == '__main__':
    dashboard = NamesDashboard()
    dashboard.run_server(debug=True, port=8050, host="127.0.0.1")
