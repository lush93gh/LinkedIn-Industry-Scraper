# LinkedIn Industry Scraper

Scrape every publicly discoverable LinkedIn profile for a given **industry** and export results to CSV and SQLite.

## ⚖️ Legal & Ethical Notice

*This tool is provided for educational purposes only.* Automated scraping of LinkedIn may violate the [LinkedIn Terms of Service](https://www.linkedin.com/legal/user-agreement) and local law. For commercial or high‑volume use, apply to the **[LinkedIn Partner API](https://developer.linkedin.com/)** instead. Always respect `robots.txt`, add delays, rotate user‑agents, and honour account / rate limits. We include exponential back‑off and randomized fingerprints, but you are solely responsible for compliant operation.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate  # or your OS equivalent
pip install -r requirements.txt
playwright install chromium

# Basic usage
python scrape.py --industry "Information Technology" --max-profiles 500 --concurrency 3

# With proxy & authenticated cookie
python scrape.py --industry "Finance" --proxy socks5://127.0.0.1:9050 \
                 --login-cookie '{"name":"li_at", ...}'
```
Outputs are written to output/profiles.csv and output/profiles.db by default.
