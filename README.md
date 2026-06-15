# Data Cleaning Agent

An autonomous, modular data cleaning pipeline for structured CSV datasets. Built and tested on the Adult Income dataset.

Features


Type coercion — converts columns to the correct numeric or categorical types
Missing value handling — fills numeric columns with the median and categorical columns with the mode
Outlier detection — flags outliers using the IQR method (adds flag columns, does not remove rows)
Deduplication — removes exact duplicate rows
Schema validation — asserts expected columns and types are present after cleaning


Project Structure

data-cleaning-agent/
├── agent/
│   ├── 01_loader.py
│   ├── 02_type_coercion.py
│   ├── 03_missing_values.py
│   ├── 04_outliers.py
│   ├── 05_deduplication.py
│   ├── 06_validation.py
│   └── 07_pipeline.py
├── notebooks/
│   ├── 01_data_profiling.ipynb
│   ├── 02_type_coercion.ipynb
│   ├── 03_missing_value_handling.ipynb
│   ├── 04_outlier_detection.ipynb
│   ├── 05_deduplication.ipynb
│   └── 06_validation.ipynb
├── dataset/
├── run_agent.py
├── requirement.txt
└── README.md

Setup

bash# 1. Clone the repo
git clone https://github.com/akhi-raj/data-cleaning-agent.git
cd data-cleaning-agent

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirement.txt

Usage

bashpython run_agent.py <path_to_your_dataset.csv>

Example:

bashpython run_agent.py ./dataset/adult.csv

Output

The cleaned dataset is saved as cleaned_output.csv in the project root.

Outlier columns are added as boolean flags (e.g., age_outlier) rather than removed, so you retain full control over how to handle them.

Notes


This pipeline is schema-specific. It is designed for the Adult Income dataset column structure. Running it on a different dataset without modifying the agent modules will likely cause errors or produce incorrect results.



The notebooks/ folder contains step-by-step Jupyter notebooks for each cleaning stage, useful for understanding or debugging individual steps.
