"""Write demo train.csv and test.csv under data/."""

from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    start = pd.Timestamp("2024-01-01")
    train_t = pd.date_range(start, periods=168, freq="h")
    test_t = pd.date_range(train_t[-1] + pd.Timedelta(hours=1), periods=48, freq="h")
    rng = np.random.default_rng(42)
    train_p = 100 + 15 * np.sin(2 * np.pi * np.arange(168) / 24) + rng.normal(0, 2, 168)
    test_p = 102 + 15 * np.sin(2 * np.pi * np.arange(48) / 24) + rng.normal(0, 2, 48)
    pd.DataFrame({"timestamp": train_t, "power": train_p.round(2)}).to_csv(
        DATA_DIR / "train.csv", index=False
    )
    pd.DataFrame({"timestamp": test_t, "power": test_p.round(2)}).to_csv(
        DATA_DIR / "test.csv", index=False
    )
    print("Wrote", DATA_DIR / "train.csv", DATA_DIR / "test.csv")


if __name__ == "__main__":
    main()
