import dash
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from flask import Flask
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from plotly.subplots import make_subplots

server = Flask(__name__)
app = dash.Dash(server=server, external_stylesheets=[dbc.themes.DARKLY])
app.title = "Trivsel – sammenlign skoler"
pio.templates.default = "plotly_dark"

df = pd.read_csv("data.csv").set_index("Institution")


def make_table(element_id):
    return dash_table.DataTable(
        id=element_id,
        columns=[
            {"name": name, "id": name} for name in ["Institution"] + list(df.columns)
        ],
    )


app.layout = html.Div(
    [
        html.H1("Vælg en eller flere skoler"),
        html.Div(
            dcc.Dropdown(
                id="school-input",
                options=[{"label": name, "value": name} for name in df.index],
                value=[],
                multi=True,
            )
        ),
        html.H4("Trivselsindikatorer og karakterer"),
        make_table("value-table"),
        html.H4("Percentiler"),
        make_table("percentile-table"),
        dcc.Graph(id="general-graph"),
        html.H4("Om"),
        dcc.Markdown(
            "Kilde: Uddannelsesstatistik ([trivsel](https://uddannelsesstatistik.dk/Pages/Reports/1599.aspx), "
            + "[karakterer](https://uddannelsesstatistik.dk/Pages/Reports/1802.aspx), 2021-05-30). "
            + "Kildekode: [GitHub](https://github.com/fuglede/skoler)."
        ),
    ],
    className="container",
)


@app.callback(
    Output(component_id="general-graph", component_property="figure"),
    Input(component_id="school-input", component_property="value"),
)
def update_figure(input_values):
    fig = make_subplots(
        rows=len(df.columns), cols=1, subplot_titles=df.columns, vertical_spacing=0.05,
    )

    fig.update_layout(height=2100, paper_bgcolor="#222", plot_bgcolor="#222")
    # Use all but the first color for the vertical lines in the plots.
    base_color, *colors = px.colors.qualitative.Plotly

    for row, column_name in enumerate(df.columns, 1):
        fig.add_trace(
            go.Histogram(x=df[column_name], marker_color=base_color, showlegend=False),
            row=row,
            col=1,
        )
        for i, input_value in enumerate(input_values):
            x = df.loc[input_value, column_name]
            # We could use fig.add_vline here to add the vertical lines, but that
            # leaves us with no easy way to add legends. Instead, we add them as
            # simple scatter plots with a hardcoded height and make sure we only
            # show the legend for one group of lines.
            fig.add_trace(
                go.Scatter(
                    x=[x, x],
                    y=[0, 120],
                    mode="lines",
                    line={"color": colors[i % len(colors)]},
                    name=input_value,
                    showlegend=row == 1,
                ),
                row=row,
                col=1,
            )
    return fig


@app.callback(
    Output("value-table", "data"), Input("school-input", "value"),
)
def update_value_table(institutions):
    return [
        {"Institution": institution} | dict(df.loc[institution].round(2))
        for institution in institutions
    ]


def make_rows(transformation, institutions):
    return [
        {"Institution": institution} | dict(transformation(institution))
        for institution in institutions
    ]


@app.callback(
    Output("percentile-table", "data"), Input("school-input", "value"),
)
def update_percentile_table(institutions):
    result = []
    for institution in institutions:
        this_result = {"Institution": institution}
        for col in df.columns:
            series = df[col].dropna()
            if institution in series:
                this_result[col] = round(
                    (series < series.loc[institution]).mean() * 100
                )
        result.append(this_result)
    return result


if __name__ == "__main__":
    app.run_server(debug=True)
