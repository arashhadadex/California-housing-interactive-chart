import dash
from dash import dcc, html, dash_table, Input, Output, callback
import plotly.express as px
import pandas as pd
import numpy as np

# --- Load dataset ---
df = pd.read_csv("housing.csv")
df.columns = df.columns.str.strip()  # remove any accidental whitespace

# Drop rows with missing values
df = df.dropna()

# Get unique ocean proximity values for the dropdown
ocean_options = df["ocean_proximity"].unique().tolist()

# --- App initialization ---
app = dash.Dash(__name__)
server = app.server
app.title = "California Housing Dashboard"

# --- Empty figure ---
empty_fig = {
    "data": [],
    "layout": {
        "xaxis": {"visible": False},
        "yaxis": {"visible": False},
        "annotations": [{
            "text": "No data for selected filters",
            "showarrow": False, "xref": "paper", "yref": "paper",
            "x": 0.5, "y": 0.5, "font": {"size": 16},
        }],
    },
}

# --- Theme system ---
THEMES = {
    "light": {
        "bg": "#f5f6fa", "card": "#ffffff", "text": "#2c3e50",
        "border": "#e0e0e0", "header": "#2c3e50",
        "plotly_template": "plotly_white",
    },
    "dark": {
        "bg": "#1a1d23", "card": "#2d323b", "text": "#e0e0e0",
        "border": "#404754", "header": "#ffffff",
        "plotly_template": "plotly_dark",
    },
}

# --- Layout ---
app.layout = html.Div([

    # Header
    html.Div([
        html.H1("California Housing Dashboard", id="title", style={"margin": 0, "fontSize": 28}),
        html.Div([
            dcc.RadioItems(
                id="theme-toggle",
                options=[{"label": " Light", "value": "light"}, {"label": " Dark", "value": "dark"}],
                value="light", inline=True,
                labelStyle={"marginRight": 20, "cursor": "pointer", "fontSize": 15},
            ),
        ], style={"display": "flex", "alignItems": "center"}),
    ], id="header", style={"display": "flex", "justifyContent": "space-between",
                            "alignItems": "center", "padding": "20px 30px"}),

    # KPI Row
    html.Div(id="kpi-row", style={"display": "flex", "flexWrap": "wrap", "padding": "0 20px", "gap": "10px"}),

    # Filters
    html.Div([
        html.Div([
            html.Label("Ocean Proximity", style={"fontWeight": 600, "marginBottom": 4}),
            dcc.Dropdown(
                id="ocean-dropdown",
                options=[{"label": o, "value": o} for o in ocean_options],
                value=ocean_options,
                multi=True,
            ),
        ], style={"flex": "1", "minWidth": "220px", "padding": "8px"}),

        html.Div([
            html.Label("Median Income Range", style={"fontWeight": 600, "marginBottom": 4}),
            dcc.RangeSlider(
                id="income-slider",
                min=round(df["median_income"].min(), 1),
                max=round(df["median_income"].max(), 1),
                step=0.5,
                value=[df["median_income"].min(), df["median_income"].max()],
                marks={i: str(i) for i in range(0, 16, 3)},
                tooltip={"placement": "bottom", "always_visible": True},
            ),
        ], style={"flex": "3", "minWidth": "300px", "padding": "8px"}),

    ], id="filters", style={"display": "flex", "flexWrap": "wrap", "padding": "10px 20px", "alignItems": "center"}),

    # Charts row 1
    html.Div([
        dcc.Graph(id="bar-chart"),
        dcc.Graph(id="scatter-chart"),
    ], style={"display": "flex", "flexWrap": "wrap", "padding": "0 10px"}),

    # Charts row 2
    html.Div([
        dcc.Graph(id="hist-chart"),
        dcc.Graph(id="pie-chart"),
    ], style={"display": "flex", "flexWrap": "wrap", "padding": "0 10px"}),

    # Geographic map
    html.Div([
        dcc.Graph(id="map-chart"),
    ], style={"padding": "0 10px"}),

    # Data table
    html.Div([
        html.H3("Filtered Data", id="table-title", style={"padding": "10px 20px"}),
        dash_table.DataTable(
            id="data-table",
            page_size=10,
            style_table={"overflowX": "auto"},
            sort_action="native",
            filter_action="native",
        ),
        html.Button("Download CSV", id="download-btn",
                    style={"margin": "15px 20px", "padding": "8px 20px",
                           "cursor": "pointer", "borderRadius": 4}),
        dcc.Download(id="download"),
    ], id="data-section", style={"padding": "10px"}),

], id="main-container")


# --- Callback 1: Theme ---
@callback(
    [Output("main-container", "style"), Output("header", "style"),
     Output("title", "style"), Output("table-title", "style"),
     Output("download-btn", "style")],
    Input("theme-toggle", "value"),
)
def update_theme(theme):
    t = THEMES[theme]
    return (
        {"backgroundColor": t["bg"], "minHeight": "100vh",
         "fontFamily": "Segoe UI, Helvetica, Arial, sans-serif", "color": t["text"]},
        {"display": "flex", "justifyContent": "space-between", "alignItems": "center",
         "padding": "20px 30px", "backgroundColor": t["card"],
         "borderBottom": f"1px solid {t['border']}"},
        {"margin": 0, "fontSize": 28, "color": t["header"]},
        {"padding": "10px 20px", "color": t["text"]},
        {"margin": "15px 20px", "padding": "8px 20px", "cursor": "pointer",
         "borderRadius": 4, "backgroundColor": t["card"], "color": t["text"],
         "border": f"1px solid {t['border']}"},
    )


# --- Callback 2: Main dashboard ---
@callback(
    [Output("kpi-row", "children"),
     Output("bar-chart", "figure"),
     Output("scatter-chart", "figure"),
     Output("hist-chart", "figure"),
     Output("pie-chart", "figure"),
     Output("map-chart", "figure"),
     Output("data-table", "data"),
     Output("data-table", "columns"),
     Output("data-table", "style_data"),
     Output("data-table", "style_header"),
     Output("data-table", "style_cell")],
    [Input("ocean-dropdown", "value"),
     Input("income-slider", "value"),
     Input("theme-toggle", "value")],
)
def update_dashboard(selected_ocean, income_range, theme):
    t = THEMES[theme]
    template = t["plotly_template"]

    # --- Filter ---
    filtered_df = df[
        df["ocean_proximity"].isin(selected_ocean) &
        (df["median_income"] >= income_range[0]) &
        (df["median_income"] <= income_range[1])
    ].copy()

    # --- Empty state ---
    if filtered_df.empty:
        return ([html.Div("No data", style={"padding": 20})],
                empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, [], [], {}, {}, {})

    # --- KPIs ---
    avg_house_value = f"${filtered_df['median_house_value'].mean():,.0f}"
    avg_income      = f"{filtered_df['median_income'].mean():,.2f}"
    total_population = f"{filtered_df['population'].sum():,}"

    kpis = []
    for label, value, accent in [
        ("Avg House Value",  avg_house_value,  "#2ecc71"),
        ("Avg Median Income", avg_income,       "#3498db"),
        ("Total Population",  total_population, "#e74c3c"),
    ]:
        kpis.append(html.Div([
            html.Div(label, style={"fontSize": 13, "color": t["text"], "opacity": 0.6,
                                    "textTransform": "uppercase", "letterSpacing": "0.5px"}),
            html.Div(value, style={"fontSize": 28, "fontWeight": "bold", "color": accent}),
        ], style={"backgroundColor": t["card"], "borderRadius": 8, "padding": "20px 25px",
                  "flex": "1", "minWidth": "180px", "textAlign": "center",
                  "border": f"1px solid {t['border']}", "boxShadow": "0 1px 4px rgba(0,0,0,0.06)"}))

    # --- Bar chart: Avg house value by ocean proximity ---
    agg = filtered_df.groupby("ocean_proximity", as_index=False).agg(
        avg_value=("median_house_value", "mean"),
        avg_income=("median_income", "mean"),
    ).round(2)

    bar_fig = px.bar(
        agg, x="ocean_proximity", y="avg_value",
        title="Avg House Value by Ocean Proximity",
        color="ocean_proximity",
        color_discrete_sequence=px.colors.qualitative.Set2,
        labels={"ocean_proximity": "Ocean Proximity", "avg_value": "Avg House Value (USD)"},
        template=template,
    )
    bar_fig.update_layout(plot_bgcolor=t["card"], paper_bgcolor=t["card"],
                          font_color=t["text"], margin=dict(l=40, r=20, t=40, b=40))

    # --- Scatter: Income vs House Value ---
    scatter_fig = px.scatter(
        filtered_df.sample(min(1000, len(filtered_df))),
        x="median_income", y="median_house_value",
        color="ocean_proximity",
        title="Median Income vs House Value",
        opacity=0.4,
        hover_data=["housing_median_age", "population"],
        color_discrete_sequence=px.colors.qualitative.Set2,
        labels={"median_income": "Median Income", "median_house_value": "House Value (USD)"},
        template=template,
    )
    scatter_fig.update_layout(plot_bgcolor=t["card"], paper_bgcolor=t["card"],
                               font_color=t["text"], margin=dict(l=40, r=20, t=40, b=40))

    # --- Histogram: House value distribution ---
    hist_fig = px.histogram(
        filtered_df, x="median_house_value",
        nbins=50,
        title="House Value Distribution",
        color_discrete_sequence=["#3498db"],
        labels={"median_house_value": "Median House Value (USD)"},
        template=template,
    )
    hist_fig.update_layout(plot_bgcolor=t["card"], paper_bgcolor=t["card"],
                            font_color=t["text"], margin=dict(l=40, r=20, t=40, b=40))

    # --- Pie: Count of records by ocean proximity ---
    pie_fig = px.pie(
        filtered_df, names="ocean_proximity",
        title="Records by Ocean Proximity",
        color_discrete_sequence=px.colors.qualitative.Set2,
        template=template,
    )
    pie_fig.update_layout(plot_bgcolor=t["card"], paper_bgcolor=t["card"],
                          font_color=t["text"], margin=dict(l=20, r=20, t=40, b=20))

    # --- Geographic map ---
    map_fig = px.scatter_mapbox(
        filtered_df.sample(min(2000, len(filtered_df))),
        lat="latitude", lon="longitude",
        color="median_house_value",
        size="population",
        color_continuous_scale="plasma",
        size_max=15, zoom=5,
        title="Housing Prices by Location",
        labels={"median_house_value": "House Value (USD)"},
        mapbox_style="carto-positron",
        template=template,
    )
    map_fig.update_layout(paper_bgcolor=t["card"], font_color=t["text"],
                          margin=dict(l=0, r=0, t=40, b=0), height=500)

    # --- Data table ---
    display_cols = ["longitude", "latitude", "housing_median_age", "total_rooms",
                    "total_bedrooms", "population", "households",
                    "median_income", "median_house_value", "ocean_proximity"]
    table_df = filtered_df[display_cols].round(2)
    dt_data = table_df.to_dict("records")
    dt_columns = [{"name": c, "id": c} for c in display_cols]

    style_data   = {"backgroundColor": t["card"], "color": t["text"]}
    style_header = {"backgroundColor": t["card"], "color": t["text"], "fontWeight": "bold"}
    style_cell   = {"backgroundColor": t["card"], "color": t["text"]}

    return (kpis, bar_fig, scatter_fig, hist_fig, pie_fig, map_fig,
            dt_data, dt_columns, style_data, style_header, style_cell)


# --- Callback 3: CSV export ---
@callback(
    Output("download", "data"),
    Input("download-btn", "n_clicks"),
    [Input("ocean-dropdown", "value"),
     Input("income-slider", "value")],
    prevent_initial_call=True,
)
def download_csv(n_clicks, selected_ocean, income_range):
    if not n_clicks:
        return dash.no_update
    filtered_df = df[
        df["ocean_proximity"].isin(selected_ocean) &
        (df["median_income"] >= income_range[0]) &
        (df["median_income"] <= income_range[1])
    ].copy()
    return dcc.send_data_frame(filtered_df.to_csv, "filtered_housing_data.csv", index=False)


if __name__ == "__main__":
    app.run(debug=True)
