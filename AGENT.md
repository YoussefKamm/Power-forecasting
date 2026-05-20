# Agent instructions: Streamlit power data viewer

Use this document when implementing or extending the Streamlit app for this repository.

## Goal

Build a **Streamlit** application that, **on startup**, loads power time series from **CSV files under `data/`**, then **plots power over time** with an **obvious visual split** between **training** and **test** segments (for example: different colors *and* different line dash styles, plus a legend).

## Environment

- Target Python environment: **conda env `cursor-demo`** (path typically `...\anaconda3\envs\cursor-demo`).
- Before adding dependencies, verify they are importable in that env. Install only what is missing, into **`cursor-demo`** only.

### Required libraries

| Package      | Role                                      |
|-------------|-------------------------------------------|
| `streamlit` | App framework                             |
| `pandas`    | Load and align CSV data                   |
| `plotly`    | **Preferred** for interactive charts      |
| `matplotlib`| Acceptable alternative if Plotly unused   |

Suggested verification (PowerShell, adjust `conda.exe` if needed):

```powershell
& "$env:USERPROFILE\anaconda3\Scripts\conda.exe" run -n cursor-demo python -c "import streamlit, pandas, plotly, matplotlib; print('ok')"
```

Install missing packages into `cursor-demo` (example):

```powershell
& "$env:USERPROFILE\anaconda3\Scripts\conda.exe" install -n cursor-demo -y streamlit pandas plotly matplotlib
```

Use `conda install` when possible; if a package is only on PyPI, use `conda run -n cursor-demo pip install <package>`.

## Data layout (`data/`)

The repo expects CSV files under **`data/`** at the project root (create the folder if it is empty).

### Recommended file convention

- **`data/train.csv`** — training-period power (and timestamps).
- **`data/test.csv`** — test-period power (and timestamps).

If the project uses different names, the app should still discover **`*.csv`** in `data/` and map files to train/test using **clear rules** (for example: filenames containing `train` / `test`, or a small mapping dict in code documented in the README).

### Column expectations

Document the actual column names in `README.md` once data is fixed. The loader should:

1. Read each CSV with `pandas.read_csv`.
2. Parse the **time** column with `parse_dates=[...]` (or `pd.to_datetime` after load).
3. Sort by time ascending and drop duplicate timestamps if needed.
4. Ensure a single **power** column per file (name configurable constant at top of app, e.g. `POWER_COL = "power"`).

If both train and test share the same schema, keep one small function `load_power_csv(path) -> DataFrame` and call it twice.

## Streamlit app behavior

1. **Entrypoint**: single file e.g. `app.py` (or `streamlit_app.py`). Run with:
   ```powershell
   conda run -n cursor-demo streamlit run app.py
   ```
2. **Startup load**: at module level or inside `main()` guarded by `if __name__ == "__main__":`, load **all required CSVs immediately** when the script runs (not lazily on a button), so the first render reflects full data. Use `st.cache_data` for expensive reads if files are large, but still treat “first page load” as loading from disk into memory once per process.
3. **Plot**:
   - **Plotly**: one figure, two traces — `go.Scatter` for train and test; set different `line.color`, `line.dash`, and `name`; enable hover with time and power.
   - **Matplotlib**: two `plot` calls with `color`, `linestyle`, `label`; `legend()`, tight datetime x-axis.
4. **Visual distinction (mandatory)**:
   - Use **at least two** of: distinct **colors**, distinct **line styles** (solid vs dash), distinct **markers** (optional).
   - Add a **vertical line** or shaded region at the train/test boundary if the last train timestamp and first test timestamp are adjacent or if a single combined frame is plotted—this makes the split obvious even if colors fail for color-blind users.
5. **Errors**: if `data/` is missing or no CSVs match, show `st.error` with a short message listing expected paths/patterns.

## Project hygiene

- Add `data/` to **`.gitignore`** if datasets are large or non-public; keep a **`data/README.md`** describing filenames and columns, or a tiny **`data/sample_*.csv`** for demos if appropriate.
- Optionally pin versions in `environment.yml` or `requirements.txt` for reproducibility.

## Definition of done

- [ ] App starts without manual “load” clicks and reads from `data/*.csv` as specified.
- [ ] Chart shows training and test series with **clearly different** styling and a **legend**.
- [ ] Dependencies run in conda env **`cursor-demo`** and are documented for others.
