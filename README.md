# AliExpress E2E Automation

End-to-end test suite for AliExpress: login, search items by price, add to cart, and verify the total stays within budget.

---

## Prerequisites

- Python 3.12+
- Google Chrome installed
- Node.js (for Allure CLI)

---

## Installation

```bash
pip install -r requirements.txt
playwright install chrome
npm install -g allure-commandline
```

---

## How to Run

**Full run (5 items):**
```bash
pytest tests/test_e2e_scenario.py -v -s
```

**Light profile (1 item, quick smoke test):**
```bash
pytest tests/test_e2e_scenario.py -v -s --profile=light
```

**Full profile (explicit):**
```bash
pytest tests/test_e2e_scenario.py -v -s --profile=full
```

**View Allure report after run:**
```bash
allure serve reports
```

---

## Configuration

All technical settings live in `data/config.json`:

```json
{
  "base_url": "https://www.aliexpress.com",
  "headless": false,
  "slow_mo": 500,
  "timeout": 15000
}
```

Test data (search query, per-item budget, item limit) lives in `data/search_params.json`:

```json
[
  {
    "query": "shoes",
    "max_price_ils": 200,
    "max_price_usd": 75,
    "limit": 5
  }
]
```

The test detects the active currency from live search results and applies `max_price_ils` (₪) or `max_price_usd` ($) automatically.  
Credentials live in `data/credentials.json` (excluded from version control via `.gitignore`).

---

## Architecture

```
MissionE2E/
├── pages/                   # Page Object Model
│   ├── base_page.py         # Base class: navigation, popups, screenshots, bot detection
│   ├── login_page.py        # Login flow
│   ├── search_results_page.py  # Search, price filter, pagination
│   ├── product_page.py      # Variant selection, add to cart
│   └── cart_page.py         # Cart total verification
├── tests/
│   └── test_e2e_scenario.py # Main E2E test
├── utils/
│   ├── data_loader.py       # JSON file loader
│   └── price_parser.py      # Price string parser (shared utility)
├── data/
│   ├── config.json          # Environment configuration
│   ├── credentials.json     # Login credentials (gitignored)
│   ├── search_params.json   # Default search parameters
│   └── profiles/
│       ├── light.json       # 1 item — quick smoke test
│       └── full.json        # 5 items — full regression
├── screenshots/
│   ├── items-screenshots/   # Screenshot per added item
│   ├── cart-screenshots/    # Cart total screenshot
│   └── error-screenshots/   # Auto-captured on test failure
├── reports/                 # Allure raw results
└── conftest.py              # Fixtures, browser config, profile selection
```

### Design Principles

- **POM** — each page has its own class with locators and methods
- **OOP** — `BasePage` provides shared behavior; page classes inherit from it
- **SRP** — `price_parser.py` handles price parsing; `data_loader.py` handles file I/O
- **DDT** — test inputs (credentials, search params) are externalized to JSON files
- **Profiles** — `--profile=light/full` selects different data sets at runtime

---

## Limitations & Assumptions

- **Currency**: prices are in ₪ (ILS) as served by AliExpress Israel
- **Login**: requires real credentials — no guest/stub mode (login is part of the test requirements). A dedicated test account is included in `data/credentials.json` for reviewer convenience — in a real project these would be stored in environment variables or a secrets manager
- **CAPTCHA**: AliExpress may show a slider CAPTCHA; the test attempts to solve it automatically via JavaScript mouse simulation. If the automated solve fails, a 2-minute manual window is provided for the user to manually solve it
- **Variant selection**: variants (size, color, etc.) are chosen randomly from available (non-sold-out) options. Quantity defaults to 1
- **Cart total**: items must be selected (checkbox) in the cart before the total is calculated — the test does this automatically
- **Network**: AliExpress occasionally returns empty responses; the test retries navigation up to 3 times before failing

---

## Edge Cases Handled

| Scenario | Behaviour |
|---|---|
| Fewer than `limit` items found under `max_price` | Test continues with however many were found |
| No items found at all | Cart step is skipped gracefully — test does not crash |
| All variants of a product are sold out | Product is skipped, next URL is tried |
| Add to Cart button not available | Product is skipped, does not count toward total |
| Search results span multiple pages | Automatically navigates to next page until `limit` is reached |
| CAPTCHA appears during navigation | Automated slider solve attempted; falls back to manual if it fails |
| Network error on navigation | Retried up to 3 times with a 3-second delay between attempts |
| Promo popup on cart page | Detected and closed automatically before reading total |
