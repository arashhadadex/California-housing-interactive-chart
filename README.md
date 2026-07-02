# California Housing Dashboard

An interactive data dashboard built with Plotly Dash, exploring the California Housing dataset.

## Live Demo

[View Dashboard](https://arashhadad-california-housing-interactive-dashboard.hf.space)

## Features

- Filter by ocean proximity and median income range
- KPI cards — average house value, median income, total population
- Bar chart — average house value by ocean proximity
- Scatter plot — median income vs house value
- Histogram — house value distribution
- Pie chart — records by ocean proximity
- Geographic map — housing prices by location
- Interactive data table with sorting and filtering
- CSV export for filtered data
- Light and dark theme toggle

## Tech Stack

- [Dash](https://dash.plotly.com/) — web application framework
- [Plotly](https://plotly.com/python/) — interactive charts
- [Pandas](https://pandas.pydata.org/) — data manipulation
- [NumPy](https://numpy.org/) — numerical operations

## Dataset

California Housing dataset — 20,640 records of housing block data across California, including median house values, income levels, population, and geographic coordinates.

Original source: [StatLib Repository](https://www.dcc.fc.up.pt/~ltorgo/Regression/cal_housing.html)

## Getting Started

**1. Clone the repo**

```bash
git clone https://github.com/arashhadadex/California-housing-interactive-chart.git
cd California-housing-interactive-chart
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Run the app**

```bash
python sales_dashboard.py
```

**4. Open in browser**

```
http://127.0.0.1:8050
```

## Project Structure

```
California-housing-interactive-chart/
├── sales_dashboard.py
├── housing.csv
├── requirements.txt
├── Dockerfile
└── README.md
```

## Deployment

Deployed on [Hugging Face Spaces](https://huggingface.co/spaces/arashhadad/California-housing-interactive-dashboard) using Docker.

## License

MIT
