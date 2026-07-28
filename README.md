# Library Management — SQL Analytics & Dashboard

A data-analysis sample project: a realistic library management database queried with SQL, then summarized into an Excel dashboard with live formulas and native charts.

## What this demonstrates

| Skill | Where it shows up |
|---|---|
| **SQL** | `library_queries.sql` — joins across 4 tables, aggregation, subqueries, a CTE, and date arithmetic |
| **Data Analysis** | Overdue tracking, genre popularity, book utilization, member borrowing patterns |
| **Excel dashboard reporting** | `Library_Dashboard.xlsx` — KPI summary with live formulas (not hardcoded values), pivot-style sheets, native Excel charts |
| **Python** | `sqlite3` for database construction and querying, `pandas` for data export, `openpyxl` for the workbook |

## The database

A SQLite database (`library.db`) with realistic relational structure:
- **authors** (16 records)
- **books** (30 records, with genre, publication year, copies owned)
- **members** (60 records, with join date and membership type)
- **loans** (1,174 transactions across 19 months, with realistic patterns: popular titles borrowed far more often than others, ~12% of loans returned late or still outstanding, no Sunday loans since the library is closed)

## The SQL queries

`library_queries.sql` contains 8 queries answering real library-management questions:
1. Most borrowed books of all time
2. Currently overdue loans, with days overdue calculated
3. Monthly loan volume trend
4. Genre popularity (loans and unique borrowers)
5. Members with repeated late returns (a follow-up list), using a subquery
6. Book utilization — loans per copy owned, to flag under/over-stocked titles
7. New members by month and whether they've borrowed anything yet, using a CTE
8. Average loan duration by membership type

## The dashboard

`Library_Dashboard.xlsx` contains:
- **KPI Summary** — six key metrics computed with live Excel formulas that reference the raw data sheets (so the workbook recalculates if the underlying data changes)
- **Top Books** — bar chart of the 10 most borrowed titles
- **Monthly Trend** — line chart of loan volume over time
- **Genre Breakdown** — pie chart of loans by genre
- **Overdue Loans** — full list of currently outstanding late loans

## Repository contents

```
├── 01_build_database.py     # generates the synthetic library.db
├── library_queries.sql      # the 8 analytical queries
├── build_dashboard.py       # builds the Excel dashboard from query results
├── library.db               # the SQLite database
├── top_books.csv            # query export (feeds the dashboard)
├── monthly.csv               # query export
├── genre.csv                 # query export
├── overdue.csv                # query export
├── Library_Dashboard.xlsx    # the final dashboard workbook
└── README.md
```

## Running it yourself

```bash
pip install pandas openpyxl
python 01_build_database.py
sqlite3 library.db < library_queries.sql   # or run queries individually
python build_dashboard.py
```

## Notes

- All data is synthetic, generated with a fixed random seed for reproducibility.
- The Excel workbook's KPI formulas reference the raw-data sheets directly, so it recalculates correctly if the underlying loan data is updated or expanded.
