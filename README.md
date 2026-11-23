# Data Cleaning Agent

I built this in my spare time because I kept writing the same cleaning code for every new dataset: fix the types, fill the gaps, drop the duplicates, check what looks off. So I turned those steps into a small Python pipeline that looks at a CSV, works out what each column is, and cleans it without being told the column names first.

It started as a set of notebooks for one dataset (the UCI Adult census data, which is still included as an example). Since then I've reworked it and tested it on real business exports too, like website visitor lists from B2B tracking tools.

## What it does

Point it at a CSV file and it will:

1. **Load the file sensibly.** It figures out the delimiter (comma, semicolon, tab or pipe), whether there's a header row, and skips junk lines at the top. Common missing value markers like `?`, `NA` and `null` are treated as empty.
2. **Profile every column.** Each one is classified as numeric, text, true/false, date, or empty. It also spots ID-like columns and columns that are mostly zeros.
3. **Fix the types.** Numbers written as `$1,200`, `₹950` or `45%` become real numbers, and dates become real dates. It works out whether dates are written day first (`29/09/2026`) or month first, so `01/05/2026` ends up as the right day. Text that differs only in capitals, like `United kingdom` and `United Kingdom`, is unified to the most common spelling. If a value can't be converted, the report tells you how many were lost instead of hiding it.
4. **Remove duplicates.** By default only rows that are exactly the same are removed, ignoring row number columns (a copied row usually gets a new ID). This happens before missing values are filled, so filled values can't make different rows look identical.
5. **Fill missing values, carefully.** Numbers get the median. Text columns with only a handful of options get the most common value, and anything with more variety gets `"unknown"`. Some things are deliberately left empty: IDs, dates, columns that are more than half empty, and marker columns where a blank means something (for example a priority column that's either `High` or empty). Guessing those would do more harm than good.
6. **Flag outliers.** Unusual numbers are marked in a new column (for example `age_outlier`) using the IQR method. Nothing gets deleted, so you decide what to do with them.
7. **Check the result** and stop with a clear error if something is wrong.

## Getting started

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

Then run it on any CSV:

```bash
python run_agent.py path/to/data.csv
```

The cleaned file is saved as `cleaned_output.csv`. To choose the output name and also save a detailed report:

```bash
python run_agent.py path/to/data.csv -o cleaned.csv --report report.json
```

If it guesses the header wrong, you can tell it directly:

```bash
python run_agent.py data.csv --header      # first row is column names
python run_agent.py data.csv --no-header   # first row is data
```

## Fine-tuning with a config file

Most of the time you won't need one. But every dataset has quirks, and a small JSON file lets you override the automatic choices:

```bash
python run_agent.py path/to/data.csv -c my_config.json
```

| Option | What it does |
|--------|--------------|
| `has_header` | `true` or `false`. Leave it out to auto-detect. |
| `column_names` | Names to use when the file has no header. |
| `sep` | The delimiter. Leave it out to auto-detect. |
| `na_values` | Extra values to treat as missing. |
| `skiprows` | How many lines to skip at the top. Leave it out to auto-detect. |
| `lowercase_categoricals` | Lowercase all text columns. Off by default, since it changes your data. |
| `impute_overrides` | Pick the fill method for a column: `median`, `mode`, `unknown` or `skip`. |
| `skip_impute_columns` | Columns to leave unfilled. |
| `skip_outlier_columns` | Numeric columns that shouldn't get outlier flags. |
| `outlier_columns` | Flag only these columns. |
| `dayfirst` | `true` for DD/MM dates, `false` for MM/DD. Leave it out to detect. |
| `normalize_case_variants` | Unify spellings that differ only in capitals (default `true`). |
| `max_impute_missing_pct` | Columns emptier than this are not filled (default `0.5`). |
| `max_mode_categories` | Above this many options, text gaps get `"unknown"` instead of the most common value (default `20`). |
| `dedup_subset` | Treat rows as duplicates when these columns match (default: all columns). |
| `skip_dedup_columns` | Ignore these columns when looking for duplicates. Be careful: this makes it easier for genuinely different rows to be removed. |

A misspelled option causes an error rather than being silently ignored, so you'll know if a setting didn't apply.

## Example: the Adult census dataset

The `dataset/` folder contains the [UCI Adult (Census Income)](https://archive.ics.uci.edu/dataset/2/adult) dataset, extracted from the 1994 US Census by Ronny Kohavi and Barry Becker. It's a good test case because it has no header row, uses `?` for missing values, and has a few columns that need special handling.

```bash
python run_agent.py ./dataset/adult.test -c examples/adult_config.json -o cleaned_output.csv
```

The config in `examples/adult_config.json` adds proper column names and tells the pipeline not to fill or flag a few columns where that wouldn't make sense (such as the survey weight `fnlwgt`).

## Example: website visitor data

`examples/sample_visitor_companies.csv` is a made-up export in the format of a B2B visitor tracking tool: company, industry, website, pages visited, location and the date they were seen. Every company in it is invented. It has the kind of mess real exports have: `N/A` everywhere, padded names, a stray lowercase country, day-first dates, a duplicated row with a new ID, and empty rows at the end.

```bash
python run_agent.py examples/sample_visitor_companies.csv -o cleaned_visitors.csv
```

If you're running this on your own company data, keep it in a `private/` folder. It's already in `.gitignore`, so it won't end up in the repo by accident.

## What you get back

After a run, you'll see a short summary in the terminal: how many rows came in and went out, how many duplicates were removed, how many values were filled in each column, and a warning if any values couldn't be converted.

With `--report`, the same information is saved as JSON, along with what the pipeline decided about each column and why.

## Project layout

```
data-cleaning-agent/
├── agent/
│   ├── config.py          # All the settings and their defaults
│   ├── loader.py          # Reading the CSV and detecting its format
│   ├── profiler.py        # Working out what each column is
│   ├── parsing.py         # Turning text like "$1,200" into numbers and dates
│   ├── type_coercion.py
│   ├── deduplication.py
│   ├── missing_values.py
│   ├── outliers.py
│   ├── validation.py
│   └── pipeline.py        # Runs the steps in order
├── examples/
│   ├── adult_config.json
│   └── sample_visitor_companies.csv
├── notebooks/             # The original exploration that started this project
├── dataset/
├── tests/
├── run_agent.py
└── requirements.txt
```

## Running the tests

```bash
pip install pytest
python -m pytest tests
```

## Known limitations

- It works with CSV and similar text files only, not Excel or databases.
- The whole file is loaded into memory, so very large files may be slow.
- Automatic detection is a best guess. It works well on tidy files, but for anything unusual, check the report and add a config if needed.
- Despite the name, it follows fixed rules rather than making decisions with AI. Using an LLM to suggest a config for a new dataset is something I'd like to try next.

## Related reading

I also write about system architecture, including this [Apache OFBiz knowledge hub](https://noitechnologies.com/category/apache-ofbiz/).
