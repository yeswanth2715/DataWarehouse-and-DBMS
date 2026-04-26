from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_DIR = ROOT / "dashboard"
HTML_PATH = DASHBOARD_DIR / "revops_stakeholder_dashboard.html"
OUTPUT_DIR = DASHBOARD_DIR / "visuals"


def find_browser() -> Path:
    candidates = [
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Could not find Microsoft Edge or Google Chrome for headless export.")


def run_browser(browser: Path, args: list[str]) -> None:
    command = [str(browser), *args]
    subprocess.run(command, check=True)


def export_screenshot(browser: Path, url: str, output_path: Path, width: int = 1600, height: int = 1800) -> None:
    run_browser(
        browser,
        [
            "--headless",
            "--disable-gpu",
            "--hide-scrollbars",
            "--run-all-compositor-stages-before-draw",
            f"--window-size={width},{height}",
            "--virtual-time-budget=5000",
            f"--screenshot={output_path}",
            url,
        ],
    )


def export_pdf(browser: Path, url: str, output_path: Path) -> None:
    run_browser(
        browser,
        [
            "--headless",
            "--disable-gpu",
            "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=5000",
            f"--print-to-pdf={output_path}",
            url,
        ],
    )


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not HTML_PATH.exists():
        print(f"Dashboard HTML not found: {HTML_PATH}", file=sys.stderr)
        return 1

    browser = find_browser()
    base_url = HTML_PATH.resolve().as_uri()

    shots = [
        ("00_home.png", base_url, 1800),
        ("01_executive_overview.png", base_url + "?view=executive&mode=visual", 1320),
        ("02_product_drilldown.png", base_url + "?view=product&mode=visual", 2060),
        ("03_crm_drilldown.png", base_url + "?view=crm&mode=visual", 2020),
        ("04_finance_drilldown.png", base_url + "?view=finance&mode=visual", 2200),
    ]

    for filename, url, height in shots:
        export_screenshot(browser, url, OUTPUT_DIR / filename, height=height)

    export_pdf(browser, base_url, OUTPUT_DIR / "revops_stakeholder_dashboard.pdf")

    print(f"Visual exports created in: {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
