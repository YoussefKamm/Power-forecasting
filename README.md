# Power forecasting

Streamlit viewer for training vs test power time series from CSV files in `data/`.

## Data format

See [data/README.md](data/README.md). Default columns: `timestamp`, `power`.

## Environment

Use the **cursor-demo** conda environment:

```powershell
& "$env:USERPROFILE\anaconda3\Scripts\conda.exe" run -n cursor-demo python -c "import streamlit, pandas, plotly, matplotlib; print('ok')"
```

Install missing packages:

```powershell
& "$env:USERPROFILE\anaconda3\Scripts\conda.exe" install -n cursor-demo -y streamlit pandas plotly matplotlib
```

Or: `pip install -r requirements.txt` inside `cursor-demo`.

## Run the app

```powershell
cd "c:\Users\ASUS\Desktop\Youssef...9\Projects\Power-forecasting"
& "$env:USERPROFILE\anaconda3\Scripts\conda.exe" run -n cursor-demo streamlit run app.py
```

The app loads `data/train.csv` and `data/test.csv` on startup and plots them with distinct colors, line styles, a legend, and a train/test boundary marker.

## Agent instructions

See [AGENT.md](AGENT.md) for implementation conventions.
