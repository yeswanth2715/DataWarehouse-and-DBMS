# Dashboard Visuals

This folder stores repo-friendly visual exports of the live stakeholder dashboard.

## Best Format
- `HTML` is the source of truth because it stays interactive and easy to update.
- `PNG` is the best preview format for GitHub, VS Code, and quick sharing.
- `PDF` is useful for formal presentation handoff.

## Files
- `00_home.png`
- `01_executive_overview.png`
- `02_product_drilldown.png`
- `03_crm_drilldown.png`
- `04_finance_drilldown.png`
- `revops_stakeholder_dashboard.pdf`

## Regenerate
```powershell
.\.venv\Scripts\python.exe scripts\generate_stakeholder_dashboard.py
.\.venv\Scripts\python.exe scripts\export_dashboard_visuals.py
```
