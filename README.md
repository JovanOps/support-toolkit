# Support Toolkit – Log Analyzer

A simple CLI tool built in Python to analyze backend log files.

## Features
- Parses structured logs
- Counts log levels (INFO, WARNING, ERROR)
- Detects top error paths
- Generates:
  - JSON report
  - HTML report

## Usage

```bash
python src/main.py --file data/sample.log --top 5
