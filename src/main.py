import argparse
import json
import os
import re
import webbrowser
from collections import Counter
from datetime import datetime

LEVELS = ("INFO", "WARNING", "ERROR")

# Example log line:
# 2026-02-18 07:01:05 ERROR service=api msg="request failed" method=POST path=/login status=500 ms=231
LOG_RE = re.compile(
    r'^(?P<ts>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+'
    r'(?P<level>INFO|WARNING|ERROR)\s+'
    r'.*?\bpath=(?P<path>\S+)?'
)

def parse_args():
    p = argparse.ArgumentParser(description="Support Toolkit: simple log analyzer")
    p.add_argument("--file", required=True, help="Path to log file")
    p.add_argument("--top", type=int, default=5, help="Top N error paths to show")
    return p.parse_args()

def analyze_log(file_path: str, top_n: int):
    level_counts = Counter()
    error_paths = Counter()
    total_lines = 0
    parsed_lines = 0
    invalid_lines = 0

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Log file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            total_lines += 1
            line = line.strip()
            if not line:
                continue

            m = LOG_RE.search(line)
            if not m:
                invalid_lines += 1
                continue

            parsed_lines += 1
            level = m.group("level")
            path = m.group("path")

            level_counts[level] += 1

            if level == "ERROR" and path:
                error_paths[path] += 1

    report = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "file": file_path,
        "total_lines": total_lines,
        "parsed_lines": parsed_lines,
        "invalid_lines": invalid_lines,
        "level_counts": dict(level_counts),
        "top_error_paths": error_paths.most_common(top_n),
    }
    return report

def ensure_output_dir():
    os.makedirs("output", exist_ok=True)

def save_report(report: dict):
    ensure_output_dir()
    out_path = os.path.join("output", "report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return out_path

def save_html_report(report: dict):
    ensure_output_dir()

    out_path = os.path.join("output", "report.html")

    html_content = f"""
    <html>
    <head>
        <title>Support Toolkit Report</title>
        <style>
            body {{ font-family: Arial; margin: 40px; }}
            table {{ border-collapse: collapse; width: 50%; }}
            th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .error {{ color: red; }}
        </style>
    </head>
    <body>
        <h1>Support Toolkit Report</h1>
        <p><strong>File:</strong> {report['file']}</p>
        <p><strong>Total lines:</strong> {report['total_lines']}</p>
        <p><strong>Parsed lines:</strong> {report['parsed_lines']}</p>

        <h2>Log Levels</h2>
        <ul>
            <li>INFO: {report['level_counts'].get('INFO', 0)}</li>
            <li>WARNING: {report['level_counts'].get('WARNING', 0)}</li>
            <li class="error">ERROR: {report['level_counts'].get('ERROR', 0)}</li>
        </ul>

        <h2>Top ERROR Paths</h2>
        <table>
            <tr><th>Path</th><th>Count</th></tr>
    """

    for path, cnt in report["top_error_paths"]:
        html_content += f"<tr><td>{path}</td><td>{cnt}</td></tr>"

    html_content += """
        </table>
    </body>
    </html>
    """

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    webbrowser.open(out_path)
    return out_path

def print_summary(report: dict):
    print("\n=== Support Toolkit Report ===")
    print(f"File: {report['file']}")
    print(f"Generated: {report['generated_at']}")
    print(f"Total lines: {report['total_lines']}")
    print(f"Parsed lines: {report['parsed_lines']}")
    print(f"Invalid lines: {report['invalid_lines']}")

    print("\nLevel counts:")
    for lvl in LEVELS:
        print(f"  {lvl}: {report['level_counts'].get(lvl, 0)}")

    print("\nTop ERROR paths:")
    top = report["top_error_paths"]
    if not top:
        print("  (none)")
    else:
        for path, cnt in top:
            print(f"  {path}: {cnt}")

def main():
    args = parse_args()
    report = analyze_log(args.file, args.top)
    print_summary(report)
    out_path = save_report(report)  
    print(f"\nSaved JSON report to: {out_path}\n")
    out_path = save_html_report(report)
    print(f"\nSaved HTML report to: {out_path}\n")

if __name__ == "__main__":
    main()
