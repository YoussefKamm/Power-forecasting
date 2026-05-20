"""Streamlit app: load train/test power CSVs and plot with clear visual distinction."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent / "data"
TIME_COL = "timestamp"
POWER_COL = "power"

TIME_ALIASES = ("timestamp", "time", "datetime", "date")
POWER_ALIASES = ("power", "value", "load", "consumption")


def _resolve_column(columns: pd.Index, aliases: tuple[str, ...], preferred: str) -> str:
    if preferred in columns:
        return preferred
    lower_map = {c.lower(): c for c in columns}
    for alias in aliases:
        if alias in columns:
            return alias
        if alias in lower_map:
            return lower_map[alias]
    raise ValueError(
        f"Could not find a column matching {aliases!r} (preferred: {preferred!r}). "
        f"Found: {list(columns)}"
    )


@st.cache_data
def load_power_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    time_col = _resolve_column(df.columns, TIME_ALIASES, TIME_COL)
    power_col = _resolve_column(df.columns, POWER_ALIASES, POWER_COL)
    out = df[[time_col, power_col]].rename(columns={time_col: TIME_COL, power_col: POWER_COL})
    out[TIME_COL] = pd.to_datetime(out[TIME_COL])
    out[POWER_COL] = pd.to_numeric(out[POWER_COL], errors="coerce")
    out = out.dropna(subset=[TIME_COL, POWER_COL])
    return out.sort_values(TIME_COL).drop_duplicates(subset=[TIME_COL], keep="last")


def discover_train_test_paths() -> tuple[Path | None, Path | None, str | None]:
    if not DATA_DIR.is_dir():
        return None, None, (
            f"`{DATA_DIR}` not found. Create `data/` and add CSV files "
            "(e.g. `data/train.csv`, `data/test.csv`)."
        )

    csv_files = sorted(DATA_DIR.glob("*.csv"))
    if not csv_files:
        return None, None, (
            f"No CSV files in `{DATA_DIR}`. Expected `train.csv` and `test.csv`, "
            "or filenames containing `train` / `test`."
        )

    train_path = DATA_DIR / "train.csv"
    test_path = DATA_DIR / "test.csv"
    train = train_path if train_path.exists() else None
    test = test_path if test_path.exists() else None

    for path in csv_files:
        stem = path.stem.lower()
        if train is None and "train" in stem:
            train = path
        if test is None and "test" in stem:
            test = path

    missing = []
    if train is None:
        missing.append("training (e.g. `data/train.csv` or `*train*.csv`)")
    if test is None:
        missing.append("test (e.g. `data/test.csv` or `*test*.csv`)")
    if missing:
        return None, None, f"Missing {' and '.join(missing)} in `{DATA_DIR}`."

    return train, test, None


def build_power_figure(train_df: pd.DataFrame, test_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=train_df[TIME_COL],
            y=train_df[POWER_COL],
            mode="lines",
            name="Training",
            line=dict(color="#2563eb", width=2, dash="solid"),
            hovertemplate="Time: %{x}<br>Power: %{y:.2f}<extra>Training</extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=test_df[TIME_COL],
            y=test_df[POWER_COL],
            mode="lines",
            name="Test",
            line=dict(color="#dc2626", width=2, dash="dash"),
            hovertemplate="Time: %{x}<br>Power: %{y:.2f}<extra>Test</extra>",
        )
    )

    if not train_df.empty and not test_df.empty:
        boundary = train_df[TIME_COL].max()
        first_test = test_df[TIME_COL].min()
        if first_test >= boundary:
            fig.add_shape(
                type="rect",
                x0=boundary,
                x1=first_test,
                y0=0,
                y1=1,
                yref="paper",
                fillcolor="rgba(148, 163, 184, 0.2)",
                line_width=0,
                layer="below",
            )
        fig.add_shape(
            type="line",
            x0=boundary,
            x1=boundary,
            y0=0,
            y1=1,
            yref="paper",
            line=dict(color="#64748b", width=2, dash="dot"),
        )
        fig.add_annotation(
            x=boundary,
            y=1,
            yref="paper",
            text="Train / test boundary",
            showarrow=False,
            yanchor="bottom",
            font=dict(color="#64748b", size=11),
        )

    fig.update_layout(
        title="Power over time (training vs test)",
        xaxis_title="Time",
        yaxis_title="Power",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
        template="plotly_white",
        height=500,
    )
    return fig


def main() -> None:
    st.set_page_config(page_title="Power forecasting", layout="wide")
    st.title("Power forecasting")
    st.caption("Training and test power series loaded from `data/` on startup.")

    train_path, test_path, error = discover_train_test_paths()
    if error:
        st.error(error)
        return

    train_df = load_power_csv(str(train_path))
    test_df = load_power_csv(str(test_path))

    col1, col2, col3 = st.columns(3)
    col1.metric("Training points", len(train_df))
    col2.metric("Test points", len(test_df))
    col3.metric(
        "Train range",
        f"{train_df[TIME_COL].min():%Y-%m-%d} → {train_df[TIME_COL].max():%Y-%m-%d}",
    )

    st.plotly_chart(build_power_figure(train_df, test_df), use_container_width=True)

    with st.expander("Data sources"):
        st.write(f"**Training:** `{train_path.name}`")
        st.write(f"**Test:** `{test_path.name}`")


if __name__ == "__main__":
    main()
