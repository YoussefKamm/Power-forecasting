# Power data (`data/`)

Place training and test power time series here as CSV files.

## Expected files

| File | Description |
|------|-------------|
| `train.csv` | Training-period power |
| `test.csv` | Test-period power |

Alternative names are supported if they contain `train` or `test` in the filename (e.g. `power_train.csv`).

## Columns

| Column | Required | Notes |
|--------|----------|--------|
| `timestamp` | Yes* | Parseable datetimes; aliases: `time`, `datetime`, `date` |
| `power` | Yes* | Numeric power values; aliases: `value`, `load`, `consumption` |

\* Or an accepted alias listed above.

Rows should be sorted by time; duplicate timestamps keep the last row.

## Sample data

This folder includes `train.csv` (168 hourly points) and `test.csv` (48 hourly points) for local demos. Replace them with your own datasets as needed.
