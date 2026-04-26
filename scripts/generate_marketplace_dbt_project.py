from __future__ import annotations

import csv
import random
from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from textwrap import dedent


RNG = random.Random(2715)
WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
ROOT = WORKSPACE_ROOT / "DataWarehouse-and-DBMS" if (WORKSPACE_ROOT / "DataWarehouse-and-DBMS").exists() else WORKSPACE_ROOT


def write_text(relative_path: str, content: str) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = dedent(content).strip() + "\n"
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(normalized)


def write_csv(relative_path: str, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fmt_amount(value: float | Decimal | None) -> str:
    if value is None:
        return ""
    quantized = Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{quantized}"


def fmt_ratio(value: float | Decimal) -> str:
    quantized = Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{quantized}"


def random_loaded_at(offset: int) -> str:
    base = datetime(2026, 4, 24, 8, 0, 0)
    return (base + timedelta(minutes=offset * 11)).strftime("%Y-%m-%d %H:%M:%S")


def daterange_months(start_year: int, start_month: int, end_year: int, end_month: int) -> list[tuple[int, int]]:
    months: list[tuple[int, int]] = []
    year = start_year
    month = start_month
    while (year, month) <= (end_year, end_month):
        months.append((year, month))
        month += 1
        if month == 13:
            year += 1
            month = 1
    return months


def pick_day(year: int, month: int) -> date:
    if month == 2:
        last_day = 29 if year % 4 == 0 else 28
    elif month in {4, 6, 9, 11}:
        last_day = 30
    else:
        last_day = 31
    return date(year, month, RNG.randint(1, last_day))


def build_vendors() -> list[dict[str, object]]:
    vendors = [
        (2001, "SpreeEats", "food", "Berlin", 0.14, "2022-11-14", "active", 4.7),
        (2002, "MitteKitchen", "food", "Berlin", 0.16, "2023-01-08", "active", 4.5),
        (2003, "HafenGoods", "electronics", "Hamburg", 0.11, "2023-02-20", "active", 4.2),
        (2004, "ElbeLiving", "home", "Hamburg", 0.10, "2023-03-12", "inactive", 3.9),
        (2005, "BavariaBasics", "lifestyle", "Munich", 0.09, "2023-04-04", "active", 4.0),
        (2006, "AlpenStyle", "fashion", "Munich", 0.18, "2023-05-15", "active", 4.8),
        (2007, "MainMarket", "home", "Frankfurt", 0.12, "2023-06-10", "active", 4.1),
        (2008, "SkylineSelect", "electronics", "Frankfurt", 0.17, "2023-06-28", "suspended", 3.6),
        (2009, "PrenzlauPantry", "food", "Berlin", 0.13, "2023-07-18", "active", 4.6),
        (2010, "IsarTech", "electronics", "Munich", 0.15, "2023-08-21", "active", 4.4),
        (2011, "NordicNest", "home", "Hamburg", 0.08, "2023-09-09", "inactive", 3.8),
        (2012, "UrbanCanvas", "lifestyle", "Berlin", 0.10, "2023-10-17", "active", 4.3),
        (2013, "RheinRunway", "fashion", "Frankfurt", 0.20, "2023-11-05", "active", 4.9),
        (2014, "CityCycle", "lifestyle", "Berlin", 0.09, "2024-01-12", "active", 4.1),
        (2015, "HarborThreads", "fashion", "Hamburg", 0.19, "2024-02-14", "active", 4.5),
    ]
    rows: list[dict[str, object]] = []
    for idx, row in enumerate(vendors):
        vendor_id, vendor_name, category, city, commission_rate, onboarded_date, status, rating = row
        rows.append(
            {
                "vendor_id": vendor_id,
                "vendor_name": vendor_name if idx % 4 else f" {vendor_name} ",
                "category": category.upper() if idx % 5 == 0 else category,
                "city": city,
                "commission_rate": fmt_ratio(commission_rate),
                "onboarded_date": onboarded_date,
                "status": status,
                "rating": fmt_ratio(rating),
                "loaded_at": random_loaded_at(1500 + idx),
            }
        )
    return rows


def build_products(vendors: list[dict[str, object]]) -> list[dict[str, object]]:
    category_catalog = {
        "food": [
            "Artisan Pretzel Box",
            "Cold Brew Sampler",
            "Vegan Snack Crate",
            "Berlin Curry Sauce Kit",
            "Organic Pasta Bundle",
            "Chef's Weekly Bento",
            "Street Food Tasting Set",
            "Breakfast Pantry Pack",
            "Matcha Dessert Box",
            "Mediterranean Dip Trio",
        ],
        "electronics": [
            "Noise Cancel Headphones",
            "Portable Bluetooth Speaker",
            "USB-C Power Hub",
            "Smart Home Camera",
            "Mechanical Keyboard",
            "Wireless Charging Pad",
            "27 Inch Office Monitor",
            "Compact Gaming Mouse",
            "Smart Fitness Watch",
            "4K Streaming Stick",
        ],
        "lifestyle": [
            "Commuter Water Bottle",
            "Yoga Recovery Kit",
            "Travel Organizer Set",
            "Reflective City Backpack",
            "Desk Wellness Bundle",
            "Weekend Picnic Blanket",
            "Minimalist Journal Pack",
            "Urban Ride Helmet",
            "Scented Focus Candle",
            "Reusable Coffee Cup",
        ],
        "fashion": [
            "Tailored Wool Coat",
            "Classic Leather Belt",
            "Relaxed Linen Shirt",
            "Everyday Sneakers",
            "Merino Knit Sweater",
            "Structured Tote Bag",
            "City Runner Jacket",
            "Cashmere Scarf",
            "Slim Fit Chinos",
            "Evening Crossbody Bag",
        ],
        "home": [
            "Ceramic Dinner Set",
            "Oak Bedside Lamp",
            "Soft Throw Blanket",
            "Minimal Wall Shelf",
            "Air Purifier Mini",
            "Marble Serving Tray",
            "Kitchen Knife Trio",
            "Bathroom Towel Set",
            "Glass Storage Jars",
            "Weighted Sleep Pillow",
        ],
    }

    category_price_ranges = {
        "food": (8, 45),
        "electronics": (25, 320),
        "lifestyle": (12, 90),
        "fashion": (28, 260),
        "home": (18, 180),
    }

    rows: list[dict[str, object]] = []
    vendor_products = {
        2001: 4,
        2002: 4,
        2003: 3,
        2004: 3,
        2005: 3,
        2006: 4,
        2007: 3,
        2008: 3,
        2009: 4,
        2010: 4,
        2011: 3,
        2012: 4,
        2013: 3,
        2014: 3,
        2015: 2,
    }

    product_id = 3001
    inactive_ids = {3006, 3017, 3021, 3033, 3040, 3048}
    catalog_index: defaultdict[str, int] = defaultdict(int)

    for idx, vendor in enumerate(vendors):
        vendor_id = int(vendor["vendor_id"])
        category = str(vendor["category"]).strip().lower()
        min_price, max_price = category_price_ranges[category]
        for _ in range(vendor_products[vendor_id]):
            product_name = category_catalog[category][catalog_index[category] % len(category_catalog[category])]
            catalog_index[category] += 1
            base_price = RNG.uniform(min_price, max_price)
            stock_quantity = RNG.randint(0, 240)
            created_date = pick_day(2023 if product_id < 3036 else 2024, RNG.randint(1, 12))
            rows.append(
                {
                    "product_id": product_id,
                    "vendor_id": vendor_id,
                    "product_name": product_name if product_id % 7 else f" {product_name} ",
                    "category": category,
                    "base_price": fmt_amount(base_price),
                    "stock_quantity": stock_quantity,
                    "is_active": "false" if product_id in inactive_ids else "true",
                    "created_at": created_date.strftime("%Y-%m-%d"),
                    "loaded_at": random_loaded_at(100 + idx + product_id),
                }
            )
            product_id += 1
    return rows


def build_customers() -> list[dict[str, object]]:
    first_names = [
        "Anna",
        "Lukas",
        "Mia",
        "Jonas",
        "Lea",
        "Felix",
        "Sofia",
        "Noah",
        "Clara",
        "Elias",
        "Hannah",
        "Finn",
        "Emma",
        "Paul",
        "Mila",
        "Leon",
        "Nora",
        "Luis",
        "Ida",
        "Ben",
        "Greta",
        "Tom",
        "Lina",
        "David",
        "Sarah",
        "Max",
        "Elena",
        "Tobias",
        "Julia",
        "Samuel",
    ]
    last_names = [
        "Schneider",
        "Fischer",
        "Weber",
        "Meyer",
        "Wagner",
        "Becker",
        "Hoffmann",
        "Schulz",
        "Koch",
        "Richter",
        "Klein",
        "Wolf",
        "Neumann",
        "Schwarz",
        "Zimmermann",
        "Braun",
        "Hartmann",
        "Kruger",
        "Vogel",
        "Jager",
        "Krause",
        "Bauer",
        "Brandt",
        "Lang",
        "Dietrich",
        "Peters",
        "Otto",
        "Seidel",
        "Kramer",
        "Lorenz",
    ]

    cities = ["Berlin"] * 36 + ["Hamburg"] * 23 + ["Munich"] * 18 + ["Frankfurt"] * 13
    RNG.shuffle(cities)
    segments = ["premium"] * 27 + ["standard"] * 63
    RNG.shuffle(segments)
    channels = ["paid_search", "organic", "referral", "email", "paid_social"]
    age_groups = ["18-24", "25-34", "35-44", "45-54", "55+"]

    rows: list[dict[str, object]] = []
    base_signups = daterange_months(2023, 1, 2024, 12)

    for idx in range(90):
        customer_id = 1001 + idx
        first_name = first_names[idx % len(first_names)]
        last_name = last_names[(idx * 3) % len(last_names)]
        name = f"{first_name} {last_name}"
        email = f"{first_name.lower()}.{last_name.lower()}{idx + 1}@marketmail.de"
        signup_year, signup_month = base_signups[idx % len(base_signups)]
        signup_date = pick_day(signup_year, signup_month)
        if idx >= 85:
            duplicate_source = rows[idx - 85]
            email = str(duplicate_source["email"]).strip().lower()
            signup_date = date(2024, 12, 10 + (idx - 85))
        acquisition_channel = RNG.choice(channels)
        if idx in {7, 34, 71}:
            acquisition_channel = ""
        age_group = RNG.choice(age_groups)
        if idx in {4, 18, 22, 39, 46, 64, 77, 88}:
            age_group = ""
        customer_name = name if idx % 10 else f" {name} "
        customer_email = email if idx % 12 else f" {email.upper()} "
        city = cities[idx] if idx % 8 else f" {cities[idx]} "
        rows.append(
            {
                "customer_id": customer_id,
                "name": customer_name,
                "email": customer_email,
                "city": city,
                "signup_date": signup_date.strftime("%Y-%m-%d"),
                "acquisition_channel": acquisition_channel,
                "segment": segments[idx],
                "age_group": age_group,
                "country": "Germany",
                "loaded_at": random_loaded_at(300 + idx),
            }
        )
    return rows


def build_orders_and_items(
    customers: list[dict[str, object]],
    vendors: list[dict[str, object]],
    products: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    products_by_vendor: defaultdict[int, list[dict[str, object]]] = defaultdict(list)
    for product in products:
        products_by_vendor[int(product["vendor_id"])].append(product)

    customer_lookup = {int(row["customer_id"]): row for row in customers}
    orderable_customers = [
        int(row["customer_id"])
        for row in customers
        if int(row["customer_id"]) not in {1001, 1002, 1003, 1004, 1005, 1086, 1087, 1088, 1089, 1090, 1083, 1084, 1085}
    ]
    vendor_weights = {
        2001: 1.5,
        2002: 1.2,
        2003: 1.0,
        2004: 0.6,
        2005: 0.8,
        2006: 1.4,
        2007: 0.9,
        2008: 0.3,
        2009: 1.3,
        2010: 1.1,
        2011: 0.4,
        2012: 1.0,
        2013: 1.6,
        2014: 0.7,
        2015: 1.0,
    }

    months = daterange_months(2023, 1, 2025, 3)
    month_weights = list(range(1, len(months) + 1))
    statuses = ["completed"] * 67 + ["cancelled"] * 14 + ["refunded"] * 15
    RNG.shuffle(statuses)
    null_total_orders = {5009, 5034, 5071, 5088}

    orders: list[dict[str, object]] = []
    items: list[dict[str, object]] = []
    item_id = 7001

    for idx in range(96):
        order_id = 5001 + idx
        customer_id = RNG.choices(
            population=orderable_customers,
            weights=[
                (
                    2.7
                    if str(customer_lookup[customer_id]["segment"]) == "premium"
                    else 1.0
                )
                * {
                    "referral": 1.8,
                    "organic": 1.5,
                    "email": 1.2,
                    "paid_social": 1.0,
                    "paid_search": 0.8,
                    "": 0.6,
                }.get(str(customer_lookup[customer_id]["acquisition_channel"]), 0.7)
                for customer_id in orderable_customers
            ],
            k=1,
        )[0]
        vendor_id = RNG.choices(list(vendor_weights.keys()), weights=list(vendor_weights.values()), k=1)[0]
        status = statuses[idx]

        if idx < 94:
            year, month = RNG.choices(months, weights=month_weights, k=1)[0]
            order_date = pick_day(year, month)
        else:
            order_date = date(2026, 6 + idx - 94, 15 - idx + 94)

        vendor_products = products_by_vendor[vendor_id]
        num_items = RNG.randint(2, 4)
        selected_products = RNG.sample(vendor_products, k=num_items if num_items <= len(vendor_products) else len(vendor_products))
        gross_amount = Decimal("0.00")

        for product in selected_products:
            quantity = RNG.randint(1, 3)
            base_price = Decimal(str(product["base_price"]))
            if RNG.random() < 0.22:
                multiplier = Decimal(str(RNG.choice([0.92, 0.95, 1.08, 1.12, 1.15])))
                unit_price = (base_price * multiplier).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            else:
                unit_price = base_price
            discount_pct = RNG.choice([0, 0, 5, 10, 15])
            line_gross = unit_price * quantity
            gross_amount += line_gross
            items.append(
                {
                    "item_id": item_id,
                    "order_id": order_id,
                    "product_id": int(product["product_id"]),
                    "quantity": quantity,
                    "unit_price": fmt_amount(unit_price),
                    "discount_pct": discount_pct,
                    "loaded_at": random_loaded_at(600 + item_id),
                }
            )
            item_id += 1

        if order_id in null_total_orders:
            total_amount = None
            discount_amount = Decimal("0.00")
        else:
            discount_rate = Decimal(str(RNG.choice([0, 0.03, 0.05, 0.08, 0.10, 0.12])))
            if str(customer_lookup[customer_id]["segment"]) == "premium":
                discount_rate += Decimal("0.02")
            discount_amount = (gross_amount * discount_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            total_amount = gross_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        payment_method = RNG.choice(["credit_card", "paypal", "bank_transfer", "voucher"])
        delivery_city = str(customer_lookup[customer_id]["city"]).strip()
        if idx % 14 == 0:
            delivery_city = f" {delivery_city} "

        orders.append(
            {
                "order_id": order_id,
                "customer_id": customer_id,
                "vendor_id": vendor_id,
                "order_date": order_date.strftime("%Y-%m-%d"),
                "status": status,
                "total_amount": fmt_amount(total_amount),
                "discount_amount": fmt_amount(discount_amount),
                "payment_method": payment_method,
                "delivery_city": delivery_city,
                "loaded_at": random_loaded_at(500 + idx),
            }
        )

    return orders, items


def build_campaigns() -> list[dict[str, object]]:
    channels = ["paid_search", "organic", "referral", "email", "paid_social"]
    rows: list[dict[str, object]] = []
    campaign_id = 9001

    for channel in channels:
        for wave in range(4):
            if channel == "paid_search":
                budget = RNG.randint(6200, 9500)
                impressions = RNG.randint(180000, 320000)
                clicks = RNG.randint(2500, 4200)
                conversions = RNG.randint(45, 110)
                target_segment = "standard"
            elif channel == "referral":
                budget = RNG.randint(700, 1800)
                impressions = RNG.randint(8000, 24000)
                clicks = RNG.randint(500, 1400)
                conversions = RNG.randint(120, 260)
                target_segment = "premium"
            elif channel == "organic":
                budget = RNG.randint(1200, 2600)
                impressions = RNG.randint(30000, 90000)
                clicks = RNG.randint(1800, 3600)
                conversions = RNG.randint(180, 340)
                target_segment = RNG.choice(["premium", "standard"])
            elif channel == "email":
                budget = RNG.randint(900, 2200)
                impressions = RNG.randint(15000, 45000)
                clicks = RNG.randint(1200, 2600)
                conversions = RNG.randint(150, 290)
                target_segment = "premium"
            else:
                budget = RNG.randint(2400, 4800)
                impressions = RNG.randint(70000, 140000)
                clicks = RNG.randint(1700, 3400)
                conversions = RNG.randint(70, 160)
                target_segment = "standard"

            start_year = 2023 if wave < 2 else 2024
            start_month = (wave * 3 + channels.index(channel) + 1) % 12 + 1
            start_date = pick_day(start_year, start_month)
            end_date = start_date + timedelta(days=RNG.randint(20, 54))
            if campaign_id in {9007, 9018}:
                end_date = start_date - timedelta(days=RNG.randint(3, 12))

            rows.append(
                {
                    "campaign_id": campaign_id,
                    "campaign_name": f"{channel.replace('_', ' ').title()} Wave {wave + 1}",
                    "channel": channel,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "budget_eur": fmt_amount(budget),
                    "impressions": impressions,
                    "clicks": clicks,
                    "conversions": conversions,
                    "target_segment": target_segment,
                    "loaded_at": random_loaded_at(900 + campaign_id),
                }
            )
            campaign_id += 1
    return rows


def build_events(customers: list[dict[str, object]], products: list[dict[str, object]]) -> list[dict[str, object]]:
    orderable_customers = [
        int(row["customer_id"])
        for row in customers
        if int(row["customer_id"]) not in {1001, 1002, 1003, 1004, 1005, 1086, 1087, 1088, 1089, 1090}
    ]
    product_ids = [int(product["product_id"]) for product in products]
    session_blueprint = (
        ["bounce"] * 45
        + ["browse"] * 30
        + ["cart"] * 20
        + ["checkout"] * 15
        + ["purchase"] * 20
    )
    RNG.shuffle(session_blueprint)
    null_sessions = {4, 19, 37, 54, 72, 88, 119}

    rows: list[dict[str, object]] = []
    event_id = 12001
    base_time = datetime(2024, 1, 4, 9, 0, 0)

    for index, session_type in enumerate(session_blueprint, start=1):
        session_id = None if index in null_sessions else f"sess_{index:04d}"
        customer_id = RNG.choice(orderable_customers)
        product_id = RNG.choice(product_ids)
        device_type = "mobile" if RNG.random() < 0.60 else "desktop"
        session_start = base_time + timedelta(hours=index * 5, minutes=RNG.randint(0, 45))
        event_sequence = {
            "bounce": ["page_view"],
            "browse": ["page_view", "product_view"],
            "cart": ["page_view", "product_view", "add_to_cart"],
            "checkout": ["page_view", "product_view", "add_to_cart", "checkout_start", "checkout_complete"],
            "purchase": ["page_view", "product_view", "add_to_cart", "checkout_start", "checkout_complete", "purchase"],
        }[session_type]

        for step, event_type in enumerate(event_sequence):
            if event_type == "page_view":
                page_url = "/"
            elif event_type == "product_view":
                page_url = f"/products/{product_id}"
            elif event_type == "add_to_cart":
                page_url = f"/cart/{product_id}"
            elif event_type == "checkout_start":
                page_url = "/checkout/start"
            elif event_type == "checkout_complete":
                page_url = "/checkout/review"
            else:
                page_url = "/checkout/success"

            rows.append(
                {
                    "event_id": event_id,
                    "customer_id": customer_id,
                    "session_id": session_id or "",
                    "event_type": event_type,
                    "event_timestamp": (session_start + timedelta(minutes=step * RNG.randint(2, 7))).strftime("%Y-%m-%d %H:%M:%S"),
                    "page_url": page_url,
                    "device_type": device_type,
                    "loaded_at": random_loaded_at(1300 + event_id),
                }
            )
            event_id += 1
    return rows


def build_static_files() -> dict[str, str]:
    return {
        ".gitignore": """
        .venv/
        .user.yml
        dbt_packages/
        logs/
        target/
        warehouse/*
        !warehouse/.gitkeep
        """,
        "requirements.txt": """
        dbt-core>=1.10,<1.11
        dbt-duckdb>=1.10,<1.11
        dbt-bigquery>=1.10,<1.11
        """,
        "Dockerfile": """
        FROM python:3.11-slim

        WORKDIR /app

        COPY requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt

        COPY . .

        ENV DBT_PROFILES_DIR=/app

        CMD ["dbt", "build", "--target", "dev"]
        """,
        ".github/workflows/dbt_ci.yml": """
        name: dbt-ci

        on:
          pull_request:
          push:
            branches:
              - main

        jobs:
          duckdb-build:
            runs-on: ubuntu-latest

            steps:
              - uses: actions/checkout@v4

              - uses: actions/setup-python@v5
                with:
                  python-version: "3.11"

              - name: Install dependencies
                run: |
                  python -m pip install --upgrade pip
                  pip install -r requirements.txt

              - name: Install dbt packages
                run: dbt deps --profiles-dir .

              - name: Build on DuckDB
                run: |
                  dbt seed --target dev --profiles-dir .
                  dbt build --target dev --profiles-dir .

          bigquery-staging:
            if: github.ref == 'refs/heads/main' && secrets.DBT_GOOGLE_SERVICE_ACCOUNT_JSON != ''
            runs-on: ubuntu-latest
            needs: duckdb-build
            env:
              DBT_GCP_PROJECT: ${{ vars.DBT_GCP_PROJECT }}
              DBT_GOOGLE_SERVICE_ACCOUNT_JSON: ${{ secrets.DBT_GOOGLE_SERVICE_ACCOUNT_JSON }}

            steps:
              - uses: actions/checkout@v4

              - uses: actions/setup-python@v5
                with:
                  python-version: "3.11"

              - name: Install dependencies
                run: |
                  python -m pip install --upgrade pip
                  pip install -r requirements.txt

              - name: Install dbt packages
                run: dbt deps --profiles-dir .

              - name: Build on BigQuery staging
                run: |
                  dbt seed --target staging_env --profiles-dir .
                  dbt build --target staging_env --profiles-dir .
        """,
        "dbt_project.yml": """
        name: marketplace_analytics
        version: 1.0.0
        config-version: 2
        profile: marketplace_analytics

        model-paths: ["models"]
        analysis-paths: ["analyses"]
        test-paths: ["tests"]
        seed-paths: ["seeds"]
        macro-paths: ["macros"]
        clean-targets:
          - target
          - dbt_packages
          - logs
          - warehouse

        models:
          marketplace_analytics:
            +persist_docs:
              relation: true
              columns: true
            staging:
              +materialized: view
              +schema: staging
            intermediate:
              +materialized: ephemeral
              +schema: intermediate
            marts:
              +materialized: table
              finance:
                +schema: mart_finance
              product:
                +schema: mart_product
              crm:
                +schema: mart_crm

        seeds:
          marketplace_analytics:
            +schema: raw
            +quote_columns: false

        vars:
          cohort_spine_start: "cast('2023-01-01' as date)"
          cohort_spine_end: "cast('2025-04-01' as date)"
        """,
        "profiles.yml": """
        marketplace_analytics:
          target: dev
          outputs:
            dev:
              type: duckdb
              path: ./warehouse/marketplace_analytics.duckdb
              schema: analytics
              threads: 4

            staging_env:
              type: bigquery
              method: service-account-json
              project: "{{ env_var('DBT_GCP_PROJECT', 'marketplace-analytics-staging') }}"
              dataset: analytics
              location: EU
              keyfile_json: "{{ env_var('DBT_GOOGLE_SERVICE_ACCOUNT_JSON') }}"
              threads: 8
              priority: interactive
              job_execution_timeout_seconds: 300
              job_retries: 1

            prod:
              type: bigquery
              method: oauth
              project: "{{ env_var('DBT_GCP_PROD_PROJECT', 'marketplace-analytics-prod') }}"
              dataset: analytics
              location: EU
              threads: 8
              priority: interactive
              job_execution_timeout_seconds: 300
              job_retries: 1
        """,
        "packages.yml": """
        packages:
          - package: dbt-labs/dbt_utils
            version: [">=1.3.0", "<2.0.0"]

          - package: calogica/dbt_expectations
            version: [">=0.10.0", "<1.0.0"]

          - package: dbt-labs/codegen
            version: [">=0.12.0", "<1.0.0"]
        """,
        "macros/generate_schema_name.sql": """
        {% macro generate_schema_name(custom_schema_name, node) -%}
          {%- if custom_schema_name is none -%}
            {{ target.schema }}
          {%- else -%}
            {{ custom_schema_name | trim }}
          {%- endif -%}
        {%- endmacro %}
        """,
        "macros/safe_divide.sql": """
        {% macro safe_divide(numerator, denominator) %}
          case
            when {{ denominator }} is null or {{ denominator }} = 0 then null
            else {{ numerator }} * 1.0 / {{ denominator }}
          end
        {% endmacro %}
        """,
        "macros/classify_segment.sql": """
        {% macro classify_segment(metric_name) %}
          case
            when {{ metric_name }} > 500 then 'high'
            when {{ metric_name }} >= 200 then 'mid'
            else 'low'
          end
        {% endmacro %}
        """,
        "macros/generate_date_spine.sql": """
        {% macro generate_date_spine(datepart, start_date, end_date) %}
          {{ dbt_utils.date_spine(datepart=datepart, start_date=start_date, end_date=end_date) }}
        {% endmacro %}
        """,
        "macros/get_column_summary.sql": """
        {% macro get_column_summary(relation, column_name) %}
          select
            '{{ relation }}' as relation_name,
            '{{ column_name }}' as column_name,
            count(*) as total_rows,
            sum(case when {{ column_name }} is null then 1 else 0 end) as null_rows,
            count(distinct {{ column_name }}) as distinct_values
          from {{ relation }}
        {% endmacro %}
        """,
        "models/staging/sources.yml": """
        version: 2

        sources:
          - name: raw_marketplace
            description: Raw marketplace operational extracts landed from the MySQL source system before transformation.
            schema: raw
            tables:
              - name: customers
                description: Raw customer master records including signup metadata and acquisition source.
                loaded_at_field: loaded_at
                freshness:
                  warn_after: {count: 24, period: hour}
                  error_after: {count: 48, period: hour}
                columns:
                  - name: customer_id
                    description: Operational identifier for the customer record in the source application.
                  - name: name
                    description: Customer full name as captured at signup.
                  - name: email
                    description: Email address used by the customer account, including deliberate duplicates in the raw data.
                  - name: city
                    description: Primary delivery city declared by the customer.
                  - name: signup_date
                    description: Calendar date when the customer account was created.
                  - name: acquisition_channel
                    description: Marketing or referral channel that originally acquired the customer.
                  - name: segment
                    description: Commercial segment assigned to the customer, either premium or standard.
                  - name: age_group
                    description: Customer age band used for CRM segmentation.
                  - name: country
                    description: Country associated with the customer account.
                  - name: loaded_at
                    description: Synthetic ingestion timestamp used for source freshness monitoring.

              - name: orders
                description: Raw order header records containing order status, payment details, and monetary values.
                loaded_at_field: loaded_at
                freshness:
                  warn_after: {count: 24, period: hour}
                  error_after: {count: 48, period: hour}
                columns:
                  - name: order_id
                    description: Unique identifier for the marketplace order.
                  - name: customer_id
                    description: Customer responsible for placing the order.
                  - name: vendor_id
                    description: Fulfilment vendor associated with the order.
                  - name: order_date
                    description: Date the order was placed in the checkout flow.
                  - name: status
                    description: Raw order lifecycle state from the source system.
                  - name: total_amount
                    description: Gross order amount before applying the order-level discount.
                  - name: discount_amount
                    description: Order-level discount amount applied at checkout.
                  - name: payment_method
                    description: Payment instrument used to place the order.
                  - name: delivery_city
                    description: Destination city captured on the order.
                  - name: loaded_at
                    description: Synthetic ingestion timestamp used for source freshness monitoring.

              - name: order_items
                description: Raw line items belonging to marketplace orders.
                loaded_at_field: loaded_at
                freshness:
                  warn_after: {count: 24, period: hour}
                  error_after: {count: 48, period: hour}
                columns:
                  - name: item_id
                    description: Unique identifier for the order line item.
                  - name: order_id
                    description: Parent order identifier for the line item.
                  - name: product_id
                    description: Product purchased on the order line.
                  - name: quantity
                    description: Unit quantity purchased for the product.
                  - name: unit_price
                    description: Raw transaction unit price captured at checkout.
                  - name: discount_pct
                    description: Percentage discount applied at the line-item level.
                  - name: loaded_at
                    description: Synthetic ingestion timestamp used for source freshness monitoring.

              - name: vendors
                description: Vendor master data used to evaluate marketplace supply performance.
                loaded_at_field: loaded_at
                freshness:
                  warn_after: {count: 24, period: hour}
                  error_after: {count: 48, period: hour}
                columns:
                  - name: vendor_id
                    description: Unique vendor identifier in the marketplace platform.
                  - name: vendor_name
                    description: Public-facing vendor brand name.
                  - name: category
                    description: Primary business category assigned to the vendor.
                  - name: city
                    description: Operating city of the vendor.
                  - name: commission_rate
                    description: Marketplace commission rate charged on the vendor's orders.
                  - name: onboarded_date
                    description: Date when the vendor joined the marketplace.
                  - name: status
                    description: Operational status of the vendor partnership.
                  - name: rating
                    description: Average customer rating for the vendor.
                  - name: loaded_at
                    description: Synthetic ingestion timestamp used for source freshness monitoring.

              - name: products
                description: Product catalog records listed by vendors.
                loaded_at_field: loaded_at
                freshness:
                  warn_after: {count: 24, period: hour}
                  error_after: {count: 48, period: hour}
                columns:
                  - name: product_id
                    description: Unique identifier for the listed product.
                  - name: vendor_id
                    description: Vendor that owns the product listing.
                  - name: product_name
                    description: Customer-facing product name.
                  - name: category
                    description: Product category associated with the listing.
                  - name: base_price
                    description: Standard catalog price for the product.
                  - name: stock_quantity
                    description: Available stock quantity recorded in the source system.
                  - name: is_active
                    description: Boolean flag showing whether the product is currently active.
                  - name: created_at
                    description: Date when the product was created in the catalog.
                  - name: loaded_at
                    description: Synthetic ingestion timestamp used for source freshness monitoring.

              - name: campaigns
                description: Marketing campaign metadata and media performance metrics.
                loaded_at_field: loaded_at
                freshness:
                  warn_after: {count: 24, period: hour}
                  error_after: {count: 48, period: hour}
                columns:
                  - name: campaign_id
                    description: Unique campaign identifier from the marketing planning sheet.
                  - name: campaign_name
                    description: Business-friendly name of the campaign.
                  - name: channel
                    description: Acquisition channel where the campaign was run.
                  - name: start_date
                    description: Planned campaign launch date.
                  - name: end_date
                    description: Planned campaign end date.
                  - name: budget_eur
                    description: Budget allocated to the campaign in EUR.
                  - name: impressions
                    description: Total media impressions delivered by the campaign.
                  - name: clicks
                    description: Total clicks generated by the campaign.
                  - name: conversions
                    description: Marketing conversions reported by the campaign.
                  - name: target_segment
                    description: Customer segment the campaign was designed to acquire or retain.
                  - name: loaded_at
                    description: Synthetic ingestion timestamp used for source freshness monitoring.

              - name: events
                description: Raw clickstream events that describe the customer funnel from browse to purchase.
                loaded_at_field: loaded_at
                freshness:
                  warn_after: {count: 24, period: hour}
                  error_after: {count: 48, period: hour}
                columns:
                  - name: event_id
                    description: Unique event identifier.
                  - name: customer_id
                    description: Customer tied to the session event.
                  - name: session_id
                    description: Browser or app session identifier, with deliberate nulls in the raw feed.
                  - name: event_type
                    description: Funnel event captured in the clickstream.
                  - name: event_timestamp
                    description: Timestamp when the event happened.
                  - name: page_url
                    description: URL or logical page route where the event happened.
                  - name: device_type
                    description: Device used during the session.
                  - name: loaded_at
                    description: Synthetic ingestion timestamp used for source freshness monitoring.
        """,
        "models/staging/stg_customers.sql": """
        with source as (
            select * from {{ source('raw_marketplace', 'customers') }}
        ),

        cleaned as (
            select
                cast(customer_id as integer) as customer_id,
                trim(name) as customer_name,
                lower(trim(email)) as customer_email,
                trim(city) as city,
                cast(signup_date as date) as signup_date,
                coalesce(nullif(trim(acquisition_channel), ''), 'unknown') as acquisition_channel,
                lower(trim(segment)) as segment,
                nullif(trim(age_group), '') as age_group,
                trim(country) as country,
                cast(loaded_at as timestamp) as source_loaded_at,
                row_number() over (
                    partition by lower(trim(email))
                    order by cast(signup_date as date) desc, cast(customer_id as integer) desc
                ) as email_dedupe_rank
            from source
        )

        select
            customer_id,
            customer_name,
            customer_email,
            city,
            signup_date,
            acquisition_channel,
            segment,
            age_group,
            country,
            segment = 'premium' as is_premium,
            source_loaded_at
        from cleaned
        where email_dedupe_rank = 1
        """,
        "models/staging/stg_orders.sql": """
        with source as (
            select * from {{ source('raw_marketplace', 'orders') }}
        )

        select
            cast(order_id as integer) as order_id,
            cast(customer_id as integer) as customer_id,
            cast(vendor_id as integer) as vendor_id,
            cast(order_date as date) as order_date,
            lower(trim(status)) as order_status,
            cast(total_amount as numeric) as total_amount,
            cast(coalesce(discount_amount, 0) as numeric) as discount_amount,
            lower(trim(payment_method)) as payment_method,
            trim(delivery_city) as delivery_city,
            cast(loaded_at as timestamp) as source_loaded_at,
            cast(total_amount as numeric) - cast(coalesce(discount_amount, 0) as numeric) as net_amount,
            extract(year from cast(order_date as date)) as order_year,
            extract(month from cast(order_date as date)) as order_month,
            concat(
                cast(extract(year from cast(order_date as date)) as {{ dbt.type_string() }}),
                '-Q',
                cast(extract(quarter from cast(order_date as date)) as {{ dbt.type_string() }})
            ) as order_quarter,
            lower(trim(status)) = 'refunded' as is_refunded,
            lower(trim(status)) = 'cancelled' as is_cancelled,
            cast(order_date as date) > cast({{ dbt.current_timestamp() }} as date) as is_future_order
        from source
        where total_amount is not null
        """,
        "models/staging/stg_products.sql": """
        with source as (
            select * from {{ source('raw_marketplace', 'products') }}
        )

        select
            cast(product_id as integer) as product_id,
            cast(vendor_id as integer) as vendor_id,
            trim(product_name) as product_name,
            lower(trim(category)) as category,
            cast(base_price as numeric) as base_price,
            cast(stock_quantity as integer) as stock_quantity,
            lower(cast(is_active as {{ dbt.type_string() }})) = 'true' as is_active,
            cast(created_at as date) as created_at,
            cast(loaded_at as timestamp) as source_loaded_at,
            case
                when cast(base_price as numeric) < 20 then 'budget'
                when cast(base_price as numeric) <= 100 then 'mid'
                else 'premium'
            end as price_tier
        from source
        """,
        "models/staging/stg_order_items.sql": """
        with source as (
            select * from {{ source('raw_marketplace', 'order_items') }}
        ),

        typed as (
            select
                cast(item_id as integer) as item_id,
                cast(order_id as integer) as order_id,
                cast(product_id as integer) as product_id,
                cast(quantity as integer) as quantity,
                cast(unit_price as numeric) as unit_price,
                cast(discount_pct as numeric) as discount_pct,
                cast(loaded_at as timestamp) as source_loaded_at
            from source
        ),

        joined as (
            select
                typed.*,
                products.base_price,
                products.is_active as product_is_active
            from typed
            inner join {{ ref('stg_orders') }} as orders
                on typed.order_id = orders.order_id
            left join {{ ref('stg_products') }} as products
                on typed.product_id = products.product_id
        )

        select
            item_id,
            order_id,
            product_id,
            quantity,
            unit_price,
            discount_pct,
            source_loaded_at,
            quantity * unit_price * (1 - coalesce(discount_pct, 0) / 100.0) as line_total,
            base_price,
            product_is_active,
            case
                when base_price is null then null
                when abs(unit_price - base_price) > 0.01 then true
                else false
            end as is_price_inconsistent
        from joined
        """,
        "models/staging/stg_vendors.sql": """
        with source as (
            select * from {{ source('raw_marketplace', 'vendors') }}
        )

        select
            cast(vendor_id as integer) as vendor_id,
            trim(vendor_name) as vendor_name,
            lower(trim(category)) as vendor_category,
            trim(city) as city,
            cast(commission_rate as numeric) as commission_rate,
            cast(onboarded_date as date) as onboarded_date,
            lower(trim(status)) as vendor_status,
            cast(rating as numeric) as rating,
            cast(loaded_at as timestamp) as source_loaded_at,
            lower(trim(status)) in ('inactive', 'suspended') as is_vendor_inactive_or_suspended
        from source
        """,
        "models/staging/stg_campaigns.sql": """
        with source as (
            select * from {{ source('raw_marketplace', 'campaigns') }}
        )

        select
            cast(campaign_id as integer) as campaign_id,
            trim(campaign_name) as campaign_name,
            lower(trim(channel)) as channel,
            cast(start_date as date) as start_date,
            cast(end_date as date) as end_date,
            cast(budget_eur as numeric) as budget_eur,
            cast(impressions as integer) as impressions,
            cast(clicks as integer) as clicks,
            cast(conversions as integer) as conversions,
            lower(trim(target_segment)) as target_segment,
            cast(loaded_at as timestamp) as source_loaded_at,
            {{ safe_divide('cast(clicks as numeric)', 'cast(impressions as numeric)') }} as ctr,
            {{ safe_divide('cast(conversions as numeric)', 'cast(clicks as numeric)') }} as cvr,
            cast(end_date as date) < cast(start_date as date) as is_date_error
        from source
        """,
        "models/staging/stg_events.sql": """
        with source as (
            select * from {{ source('raw_marketplace', 'events') }}
        ),

        typed as (
            select
                cast(event_id as integer) as event_id,
                cast(customer_id as integer) as customer_id,
                coalesce(nullif(trim(session_id), ''), 'unknown_session') as session_id,
                lower(trim(event_type)) as event_type,
                cast(event_timestamp as timestamp) as event_timestamp,
                trim(page_url) as page_url,
                lower(trim(device_type)) as device_type,
                cast(loaded_at as timestamp) as source_loaded_at
            from source
        )

        select
            event_id,
            customer_id,
            session_id,
            event_type,
            event_timestamp,
            cast(event_timestamp as date) as event_date,
            page_url,
            device_type,
            source_loaded_at,
            row_number() over (
                partition by session_id
                order by event_timestamp, event_id
            ) as event_rank_in_session,
            case
                when event_type = 'page_view' then 1
                when event_type = 'product_view' then 2
                when event_type = 'add_to_cart' then 3
                when event_type in ('checkout_start', 'checkout_complete') then 4
                when event_type = 'purchase' then 5
                else null
            end as funnel_step
        from typed
        """,
        "models/intermediate/int_orders_enriched.sql": """
        with orders as (
            select * from {{ ref('stg_orders') }}
            where not is_future_order
        ),

        customers as (
            select * from {{ ref('stg_customers') }}
        ),

        vendors as (
            select * from {{ ref('stg_vendors') }}
        ),

        joined as (
            select
                orders.*,
                customers.customer_name,
                customers.customer_email,
                customers.city as customer_city,
                customers.signup_date,
                customers.segment as customer_segment,
                customers.acquisition_channel,
                customers.is_premium,
                vendors.vendor_name,
                vendors.vendor_category,
                vendors.city as vendor_city,
                vendors.commission_rate,
                vendors.vendor_status,
                vendors.rating as vendor_rating,
                min(orders.order_date) over (partition by orders.customer_id) as first_order_date
            from orders
            left join customers
                on orders.customer_id = customers.customer_id
            left join vendors
                on orders.vendor_id = vendors.vendor_id
        )

        select
            *,
            net_amount * commission_rate as vendor_revenue,
            {{ dbt.datediff('signup_date', 'first_order_date', 'day') }} as days_to_order
        from joined
        """,
        "models/intermediate/int_customer_orders_summary.sql": """
        with customers as (
            select * from {{ ref('stg_customers') }}
        ),

        orders as (
            select
                customer_id,
                order_id,
                order_date,
                order_status,
                case
                    when is_cancelled then 0
                    when is_refunded then 0
                    else net_amount
                end as realized_amount
            from {{ ref('int_orders_enriched') }}
        ),

        aggregated as (
            select
                customers.customer_id,
                count(orders.order_id) as total_orders,
                coalesce(sum(orders.realized_amount), 0) as total_spend,
                {{ safe_divide('sum(orders.realized_amount)', 'count(orders.order_id)') }} as avg_order_value,
                min(orders.order_date) as first_order_date,
                max(orders.order_date) as last_order_date
            from customers
            left join orders
                on customers.customer_id = orders.customer_id
            group by customers.customer_id
        ),

        as_of as (
            select cast({{ dbt.current_timestamp() }} as date) as as_of_date
        )

        select
            aggregated.customer_id,
            aggregated.total_orders,
            aggregated.total_spend,
            aggregated.avg_order_value,
            aggregated.first_order_date,
            aggregated.last_order_date,
            case
                when aggregated.last_order_date is null then null
                else {{ dbt.datediff('aggregated.last_order_date', 'as_of.as_of_date', 'day') }}
            end as days_since_last_order,
            case
                when aggregated.last_order_date is null then true
                when {{ dbt.datediff('aggregated.last_order_date', 'as_of.as_of_date', 'day') }} > 90 then true
                else false
            end as churn_flag,
            {{ classify_segment('aggregated.total_spend') }} as ltv_segment
        from aggregated
        cross join as_of
        """,
        "models/intermediate/int_campaign_performance.sql": """
        with campaigns as (
            select * from {{ ref('stg_campaigns') }}
            where not is_date_error
        ),

        orders as (
            select
                order_id,
                customer_id,
                order_date,
                customer_segment,
                acquisition_channel,
                case
                    when is_cancelled then 0
                    when is_refunded then 0
                    else net_amount
                end as attributed_amount
            from {{ ref('int_orders_enriched') }}
        )

        select
            campaigns.campaign_id,
            campaigns.campaign_name,
            campaigns.channel,
            campaigns.start_date,
            campaigns.end_date,
            campaigns.budget_eur,
            campaigns.impressions,
            campaigns.clicks,
            campaigns.conversions,
            campaigns.target_segment,
            campaigns.ctr,
            campaigns.cvr,
            coalesce(sum(orders.attributed_amount), 0) as revenue_attributed,
            {{ safe_divide('coalesce(sum(orders.attributed_amount), 0)', 'campaigns.budget_eur') }} as roas,
            {{ safe_divide('campaigns.budget_eur', 'campaigns.conversions') }} as cost_per_conversion,
            {{ safe_divide('count(distinct orders.customer_id)', 'campaigns.conversions') }} as conversion_match_rate,
            {{ safe_divide('count(distinct orders.order_id)', 'campaigns.clicks') }} as click_to_order_rate,
            {{ safe_divide('count(distinct orders.customer_id)', 'campaigns.clicks') }} as click_to_customer_rate,
            {{ safe_divide('count(distinct orders.order_id)', 'campaigns.impressions') }} as impression_to_order_rate,
            coalesce(sum(orders.attributed_amount), 0) > campaigns.budget_eur * 3 as high_performing
        from campaigns
        left join orders
            on campaigns.channel = orders.acquisition_channel
            and orders.order_date between campaigns.start_date and campaigns.end_date
            and orders.customer_segment = campaigns.target_segment
        group by
            campaigns.campaign_id,
            campaigns.campaign_name,
            campaigns.channel,
            campaigns.start_date,
            campaigns.end_date,
            campaigns.budget_eur,
            campaigns.impressions,
            campaigns.clicks,
            campaigns.conversions,
            campaigns.target_segment,
            campaigns.ctr,
            campaigns.cvr
        """,
        "models/intermediate/int_funnel_sessions.sql": """
        with events as (
            select * from {{ ref('stg_events') }}
            where session_id <> 'unknown_session'
        ),

        session_rollup as (
            select
                session_id,
                customer_id,
                min(event_timestamp) as session_started_at,
                max(funnel_step) as max_funnel_step,
                max(case when funnel_step >= 1 then 1 else 0 end) as reached_page_view,
                max(case when funnel_step >= 2 then 1 else 0 end) as reached_product_view,
                max(case when funnel_step >= 3 then 1 else 0 end) as reached_add_to_cart,
                max(case when funnel_step >= 4 then 1 else 0 end) as reached_checkout,
                max(case when funnel_step = 5 then 1 else 0 end) as reached_purchase,
                min(device_type) as device_type,
                count(*) as session_event_count
            from events
            group by session_id, customer_id
        )

        select
            session_rollup.*,
            session_rollup.reached_purchase = 1 as conversion_flag,
            customers.acquisition_channel,
            customers.segment as customer_segment,
            customers.city
        from session_rollup
        left join {{ ref('stg_customers') }} as customers
            on session_rollup.customer_id = customers.customer_id
        """,
        "models/marts/finance/mart_revenue.sql": """
        with orders as (
            select *
            from {{ ref('int_orders_enriched') }}
            where not is_future_order
              and not is_cancelled
        ),

        monthly as (
            select
                extract(year from order_date) as year,
                extract(month from order_date) as month,
                extract(quarter from order_date) as quarter,
                sum(total_amount) as gross_revenue,
                sum(discount_amount) as total_discounts,
                sum(net_amount) as net_revenue,
                sum(case when is_refunded then net_amount else 0 end) as refund_amount,
                sum(net_amount) - sum(case when is_refunded then net_amount else 0 end) as net_revenue_after_refunds,
                count(order_id) as order_count,
                {{ safe_divide(
                    "sum(net_amount) - sum(case when is_refunded then net_amount else 0 end)",
                    "count(order_id)"
                ) }} as avg_order_value
            from orders
            group by 1, 2, 3
        )

        select
            *,
            {{ safe_divide(
                "net_revenue_after_refunds - lag(net_revenue_after_refunds) over (order by year, month)",
                "lag(net_revenue_after_refunds) over (order by year, month)"
            ) }} as mom_growth_pct
        from monthly
        order by year, month
        """,
        "models/marts/finance/mart_vendor_performance.sql": """
        with orders as (
            select *
            from {{ ref('int_orders_enriched') }}
            where not is_future_order
              and not is_cancelled
        ),

        vendor_summary as (
            select
                vendor_id,
                vendor_name,
                vendor_category,
                vendor_status,
                avg(vendor_rating) as avg_rating,
                sum(total_amount) as gmv,
                sum(case when is_refunded then 0 else vendor_revenue end) as vendor_revenue,
                count(order_id) as order_count,
                {{ safe_divide(
                    "sum(case when is_refunded then 1 else 0 end)",
                    "count(order_id)"
                ) }} as return_rate
            from orders
            group by vendor_id, vendor_name, vendor_category, vendor_status
        )

        select
            *,
            dense_rank() over (order by gmv desc) as gmv_rank,
            ntile(5) over (order by gmv asc) = 1 as underperforming
        from vendor_summary
        """,
        "models/marts/product/mart_funnel_analysis.sql": """
        with sessions as (
            select *
            from {{ ref('int_funnel_sessions') }}
        ),

        aggregated as (
            select
                acquisition_channel as channel,
                device_type,
                1 as step_order,
                'page_view' as funnel_stage,
                sum(case when max_funnel_step >= 1 then 1 else 0 end) as sessions_at_step,
                sum(case when reached_purchase = 1 then 1 else 0 end) as purchase_sessions
            from sessions
            group by 1, 2

            union all

            select
                acquisition_channel as channel,
                device_type,
                2 as step_order,
                'product_view' as funnel_stage,
                sum(case when max_funnel_step >= 2 then 1 else 0 end) as sessions_at_step,
                sum(case when reached_purchase = 1 then 1 else 0 end) as purchase_sessions
            from sessions
            group by 1, 2

            union all

            select
                acquisition_channel as channel,
                device_type,
                3 as step_order,
                'add_to_cart' as funnel_stage,
                sum(case when max_funnel_step >= 3 then 1 else 0 end) as sessions_at_step,
                sum(case when reached_purchase = 1 then 1 else 0 end) as purchase_sessions
            from sessions
            group by 1, 2

            union all

            select
                acquisition_channel as channel,
                device_type,
                4 as step_order,
                'checkout' as funnel_stage,
                sum(case when max_funnel_step >= 4 then 1 else 0 end) as sessions_at_step,
                sum(case when reached_purchase = 1 then 1 else 0 end) as purchase_sessions
            from sessions
            group by 1, 2

            union all

            select
                acquisition_channel as channel,
                device_type,
                5 as step_order,
                'purchase' as funnel_stage,
                sum(case when max_funnel_step >= 5 then 1 else 0 end) as sessions_at_step,
                sum(case when reached_purchase = 1 then 1 else 0 end) as purchase_sessions
            from sessions
            group by 1, 2
        ),

        funnel as (
            select
                channel,
                device_type,
                step_order,
                funnel_stage,
                sessions_at_step,
                {{ safe_divide(
                    "sessions_at_step - lead(sessions_at_step) over (partition by channel, device_type order by step_order)",
                    "sessions_at_step"
                ) }} as drop_off_rate,
                {{ safe_divide("purchase_sessions", "sessions_at_step") }} as conversion_rate_to_purchase
            from aggregated
        ),

        channel_dropoff as (
            select
                channel,
                funnel_stage,
                step_order,
                avg(drop_off_rate) as avg_drop_off_rate,
                row_number() over (
                    partition by channel
                    order by avg(drop_off_rate) desc nulls last, step_order
                ) as drop_off_rank
            from funnel
            where step_order < 5
            group by channel, funnel_stage, step_order
        )

        select
            funnel.*,
            channel_dropoff.funnel_stage as biggest_dropoff_step_for_channel,
            channel_dropoff.avg_drop_off_rate as biggest_dropoff_rate_for_channel
        from funnel
        left join channel_dropoff
            on funnel.channel = channel_dropoff.channel
           and channel_dropoff.drop_off_rank = 1
        order by channel, device_type, step_order
        """,
        "models/marts/product/mart_campaign_roi.sql": """
        select
            campaign_id,
            campaign_name,
            channel,
            target_segment,
            start_date,
            end_date,
            budget_eur,
            impressions,
            clicks,
            conversions,
            ctr,
            cvr,
            revenue_attributed as attributed_revenue,
            roas,
            cost_per_conversion,
            case
                when roas >= 5 then 'excellent'
                when roas >= 2 then 'good'
                else 'poor'
            end as roi_tier,
            high_performing
        from {{ ref('int_campaign_performance') }}
        """,
        "models/marts/crm/mart_customer_segments.sql": """
        with customers as (
            select *
            from {{ ref('stg_customers') }}
        ),

        customer_summary as (
            select *
            from {{ ref('int_customer_orders_summary') }}
        )

        select
            customers.customer_id,
            customers.customer_name,
            customers.customer_email,
            customers.segment,
            customer_summary.ltv_segment,
            customer_summary.churn_flag,
            customers.acquisition_channel,
            customers.city,
            customers.age_group,
            customers.country,
            customers.is_premium,
            coalesce(customer_summary.total_orders, 0) as total_orders,
            coalesce(customer_summary.total_spend, 0) as total_spend,
            customer_summary.avg_order_value,
            customer_summary.first_order_date,
            customer_summary.last_order_date,
            customer_summary.days_since_last_order,
            case
                when customer_summary.days_since_last_order is null then 'churned'
                when customer_summary.days_since_last_order <= 30 then 'new'
                when customer_summary.days_since_last_order <= 90 then 'active'
                when customer_summary.days_since_last_order <= 180 then 'at_risk'
                else 'churned'
            end as retention_band
        from customers
        left join customer_summary
            on customers.customer_id = customer_summary.customer_id
        """,
        "models/marts/crm/mart_cohort_retention.sql": """
        with cohort_customers as (
            select
                customer_id,
                cast({{ dbt.date_trunc('month', 'signup_date') }} as date) as cohort_month
            from {{ ref('stg_customers') }}
        ),

        month_spine as (
            {{ generate_date_spine(
                datepart='month',
                start_date=var('cohort_spine_start'),
                end_date=var('cohort_spine_end')
            ) }}
        ),

        cohort_calendar as (
            select
                cohort_months.cohort_month,
                cast(month_spine.date_month as date) as activity_month
            from (
                select distinct cohort_month
                from cohort_customers
            ) as cohort_months
            join month_spine
                on cast(month_spine.date_month as date) >= cohort_months.cohort_month
        ),

        order_activity as (
            select distinct
                customer_id,
                cast({{ dbt.date_trunc('month', 'order_date') }} as date) as activity_month
            from {{ ref('int_orders_enriched') }}
            where not is_cancelled
              and not is_future_order
        ),

        cohort_size as (
            select
                cohort_month,
                count(*) as cohort_size
            from cohort_customers
            group by cohort_month
        ),

        retention as (
            select
                cohort_calendar.cohort_month,
                {{ dbt.datediff('cohort_calendar.cohort_month', 'cohort_calendar.activity_month', 'month') }} as months_since_signup,
                count(distinct order_activity.customer_id) as retained_customers
            from cohort_calendar
            join cohort_customers
                on cohort_calendar.cohort_month = cohort_customers.cohort_month
            left join order_activity
                on cohort_customers.customer_id = order_activity.customer_id
               and cohort_calendar.activity_month = order_activity.activity_month
            group by cohort_calendar.cohort_month, cohort_calendar.activity_month
        )

        select
            retention.cohort_month,
            retention.months_since_signup,
            cohort_size.cohort_size,
            retention.retained_customers,
            {{ safe_divide('retention.retained_customers', 'cohort_size.cohort_size') }} as retention_rate
        from retention
        join cohort_size
            on retention.cohort_month = cohort_size.cohort_month
        order by retention.cohort_month, retention.months_since_signup
        """,
        "models/staging/schema.yml": """
        version: 2

        models:
          - name: stg_customers
            description: Cleaned and deduplicated customer dimension used across CRM, revenue, and funnel analysis.
            columns:
              - name: customer_id
                description: Surviving customer identifier after email-level deduplication.
                tests:
                  - not_null
                  - unique
              - name: customer_name
                description: Trimmed customer full name for reporting.
              - name: customer_email
                description: Lowercased and trimmed email address used as the deduplication key.
              - name: city
                description: Cleaned delivery city for the customer.
              - name: signup_date
                description: Customer signup date used for cohorting and time-to-first-order analysis.
              - name: acquisition_channel
                description: Acquisition source after null handling and standardization.
                tests:
                  - accepted_values:
                      values: ['paid_search', 'organic', 'referral', 'email', 'paid_social', 'unknown']
              - name: segment
                description: Customer commercial segment.
                tests:
                  - accepted_values:
                      values: ['premium', 'standard']
              - name: age_group
                description: Customer age band when available.
              - name: country
                description: Customer country.
              - name: is_premium
                description: Boolean premium flag derived from the source segment.
              - name: source_loaded_at
                description: Ingestion timestamp carried from the raw seed.

          - name: stg_orders
            description: Typed order header records with cleaned status flags and revenue fields for downstream finance analysis.
            columns:
              - name: order_id
                description: Unique order identifier.
                tests:
                  - not_null
                  - unique
              - name: customer_id
                description: Customer identifier tied to the order.
                tests:
                  - not_null
                  - relationships:
                      to: ref('stg_customers')
                      field: customer_id
                  - dbt_expectations.expect_column_proportion_of_unique_values_to_be_between:
                      min_value: 0.30
                      max_value: 0.95
              - name: vendor_id
                description: Vendor identifier tied to the order.
                tests:
                  - not_null
                  - relationships:
                      to: ref('stg_vendors')
                      field: vendor_id
              - name: order_date
                description: Cleaned order date.
              - name: order_status
                description: Normalized order lifecycle state.
                tests:
                  - accepted_values:
                      values: ['completed', 'cancelled', 'refunded']
              - name: total_amount
                description: Gross order amount after filtering out null rows.
                tests:
                  - dbt_expectations.expect_column_values_to_be_between:
                      min_value: 0
                      max_value: 2000
              - name: discount_amount
                description: Order-level discount amount.
                tests:
                  - dbt_expectations.expect_column_values_to_be_between:
                      min_value: 0
                      max_value: 300
              - name: payment_method
                description: Normalized payment method.
                tests:
                  - accepted_values:
                      values: ['credit_card', 'paypal', 'bank_transfer', 'voucher']
              - name: delivery_city
                description: Cleaned delivery city captured on the order.
              - name: source_loaded_at
                description: Ingestion timestamp carried from the raw seed.
              - name: net_amount
                description: Net order amount after subtracting the order-level discount.
              - name: order_year
                description: Calendar year extracted from the order date.
              - name: order_month
                description: Calendar month extracted from the order date.
              - name: order_quarter
                description: Year-quarter label for revenue trending.
              - name: is_refunded
                description: Boolean flag for refunded orders.
              - name: is_cancelled
                description: Boolean flag for cancelled orders.
              - name: is_future_order
                description: Boolean flag for orders dated beyond the current runtime.

          - name: stg_products
            description: Cleaned product catalog with pricing tiers and active-state normalization.
            columns:
              - name: product_id
                description: Unique product identifier.
                tests:
                  - not_null
                  - unique
              - name: vendor_id
                description: Owning vendor for the product.
                tests:
                  - relationships:
                      to: ref('stg_vendors')
                      field: vendor_id
              - name: product_name
                description: Trimmed product display name.
              - name: category
                description: Normalized product category.
              - name: base_price
                description: Standard catalog price for the product.
                tests:
                  - dbt_expectations.expect_column_values_to_be_between:
                      min_value: 0
                      max_value: 500
              - name: stock_quantity
                description: Source stock quantity.
              - name: is_active
                description: Boolean active-state flag.
              - name: created_at
                description: Product creation date.
              - name: source_loaded_at
                description: Ingestion timestamp carried from the raw seed.
              - name: price_tier
                description: Derived pricing tier for segmentation.
                tests:
                  - accepted_values:
                      values: ['budget', 'mid', 'premium']

          - name: stg_order_items
            description: Typed order line items enriched with product pricing to expose raw transaction inconsistencies.
            columns:
              - name: item_id
                description: Unique order item identifier.
                tests:
                  - not_null
                  - unique
              - name: order_id
                description: Parent order identifier.
                tests:
                  - not_null
                  - relationships:
                      to: ref('stg_orders')
                      field: order_id
              - name: product_id
                description: Ordered product identifier.
                tests:
                  - not_null
                  - relationships:
                      to: ref('stg_products')
                      field: product_id
              - name: quantity
                description: Ordered quantity.
                tests:
                  - dbt_expectations.expect_column_values_to_be_between:
                      min_value: 1
                      max_value: 10
              - name: unit_price
                description: Transaction unit price on the line item.
                tests:
                  - dbt_expectations.expect_column_values_to_be_between:
                      min_value: 0
                      max_value: 500
              - name: discount_pct
                description: Percentage discount applied to the line item.
                tests:
                  - dbt_expectations.expect_column_values_to_be_between:
                      min_value: 0
                      max_value: 100
              - name: source_loaded_at
                description: Ingestion timestamp carried from the raw seed.
              - name: line_total
                description: Net line-item revenue after item-level discount.
              - name: base_price
                description: Catalog price joined from the cleaned products model.
              - name: product_is_active
                description: Product active-state flag pulled from the product dimension.
              - name: is_price_inconsistent
                description: Boolean flag when the transaction price does not match the catalog base price.

          - name: stg_vendors
            description: Cleaned vendor dimension used for performance, commission, and supply health analysis.
            columns:
              - name: vendor_id
                description: Unique vendor identifier.
                tests:
                  - not_null
                  - unique
              - name: vendor_name
                description: Cleaned vendor display name.
              - name: vendor_category
                description: Normalized vendor business category.
              - name: city
                description: Vendor operating city.
              - name: commission_rate
                description: Marketplace commission rate as a decimal share of order value.
                tests:
                  - dbt_expectations.expect_column_values_to_be_between:
                      min_value: 0
                      max_value: 1
              - name: onboarded_date
                description: Vendor onboarding date.
              - name: vendor_status
                description: Current vendor operating status.
                tests:
                  - accepted_values:
                      values: ['active', 'inactive', 'suspended']
              - name: rating
                description: Vendor customer rating.
                tests:
                  - dbt_expectations.expect_column_values_to_be_between:
                      min_value: 0
                      max_value: 5
              - name: source_loaded_at
                description: Ingestion timestamp carried from the raw seed.
              - name: is_vendor_inactive_or_suspended
                description: Convenience flag for operationally risky vendors.

          - name: stg_campaigns
            description: Marketing campaign staging layer with cleaned dates and derived media efficiency metrics.
            columns:
              - name: campaign_id
                description: Unique campaign identifier.
                tests:
                  - not_null
                  - unique
              - name: campaign_name
                description: Business-friendly campaign name.
              - name: channel
                description: Normalized acquisition channel.
                tests:
                  - accepted_values:
                      values: ['paid_search', 'organic', 'referral', 'email', 'paid_social']
              - name: start_date
                description: Campaign start date.
              - name: end_date
                description: Campaign end date.
              - name: budget_eur
                description: Campaign budget in EUR.
                tests:
                  - dbt_expectations.expect_column_values_to_be_between:
                      min_value: 0
                      max_value: 20000
              - name: impressions
                description: Campaign impressions.
              - name: clicks
                description: Campaign clicks.
              - name: conversions
                description: Campaign conversions.
              - name: target_segment
                description: Customer segment targeted by the campaign.
                tests:
                  - accepted_values:
                      values: ['premium', 'standard']
              - name: source_loaded_at
                description: Ingestion timestamp carried from the raw seed.
              - name: ctr
                description: Click-through rate derived from clicks and impressions.
              - name: cvr
                description: Conversion rate derived from conversions and clicks.
              - name: is_date_error
                description: Boolean flag when the campaign ends before it starts.

          - name: stg_events
            description: Session-level clickstream event staging model with funnel ranking and cleaned session identifiers.
            columns:
              - name: event_id
                description: Unique event identifier.
                tests:
                  - not_null
                  - unique
              - name: customer_id
                description: Customer who generated the event.
                tests:
                  - relationships:
                      to: ref('stg_customers')
                      field: customer_id
              - name: session_id
                description: Cleaned session identifier with nulls coalesced to unknown_session.
              - name: event_type
                description: Normalized event type from the clickstream.
                tests:
                  - accepted_values:
                      values: ['page_view', 'product_view', 'add_to_cart', 'checkout_start', 'checkout_complete', 'purchase']
              - name: event_timestamp
                description: Event timestamp.
              - name: event_date
                description: Calendar date derived from the event timestamp.
              - name: page_url
                description: Page route where the event occurred.
              - name: device_type
                description: Device form factor used during the event.
                tests:
                  - accepted_values:
                      values: ['mobile', 'desktop']
              - name: source_loaded_at
                description: Ingestion timestamp carried from the raw seed.
              - name: event_rank_in_session
                description: Rank order of the event within the session.
              - name: funnel_step
                description: Integer funnel stage used to measure drop-off from browse to purchase.
        """,
        "models/intermediate/schema.yml": """
        version: 2

        models:
          - name: int_orders_enriched
            description: Order-level business logic layer combining cleaned orders with customer and vendor context.
            columns:
              - name: order_id
                description: Order identifier inherited from the staged order model.
              - name: customer_id
                description: Customer identifier linked to the order.
              - name: vendor_id
                description: Vendor identifier linked to the order.
              - name: customer_segment
                description: Customer segment joined from the customer dimension.
              - name: acquisition_channel
                description: Customer acquisition source joined from the customer dimension.
              - name: vendor_category
                description: Vendor category joined from the vendor dimension.
              - name: vendor_revenue
                description: Vendor commission revenue derived from net order value and commission rate.
              - name: days_to_order
                description: Days between signup and the customer's first order.

          - name: int_customer_orders_summary
            description: Customer-level order rollup used for churn, LTV, and segmentation logic.
            columns:
              - name: customer_id
                description: Customer identifier.
              - name: total_orders
                description: Total non-future orders linked to the customer.
              - name: total_spend
                description: Realized spend after excluding cancelled and refunded revenue.
              - name: avg_order_value
                description: Average realized order value.
              - name: first_order_date
                description: First order date for the customer.
              - name: last_order_date
                description: Most recent order date for the customer.
              - name: days_since_last_order
                description: Days since the customer last placed an order.
              - name: churn_flag
                description: Boolean flag for customers inactive for more than 90 days.
              - name: ltv_segment
                description: Customer lifetime spend segment derived from total spend.

          - name: int_campaign_performance
            description: Campaign attribution layer that aligns orders to campaigns using acquisition channel and campaign dates.
            columns:
              - name: campaign_id
                description: Campaign identifier.
              - name: revenue_attributed
                description: Revenue attributed to the campaign based on matching customer channel and order timing.
              - name: roas
                description: Return on ad spend from attributed revenue versus budget.
              - name: high_performing
                description: Boolean flag for campaigns with ROAS above 3.

          - name: int_funnel_sessions
            description: Session-level funnel rollup used to measure drop-off between event stages.
            columns:
              - name: session_id
                description: Session identifier after cleaning.
              - name: customer_id
                description: Customer tied to the session.
              - name: max_funnel_step
                description: Furthest funnel stage reached within the session.
              - name: conversion_flag
                description: Boolean flag for sessions that reached purchase.
              - name: acquisition_channel
                description: Customer acquisition source for funnel attribution.
              - name: device_type
                description: Device used during the session.
        """,
        "models/marts/finance/schema.yml": """
        version: 2

        models:
          - name: mart_revenue
            description: Monthly finance mart powering revenue, refund, discount, and growth reporting.
            tests:
              - dbt_utils.unique_combination_of_columns:
                  combination_of_columns:
                    - year
                    - month
            columns:
              - name: year
                description: Revenue year.
                tests:
                  - not_null
              - name: month
                description: Revenue month.
                tests:
                  - not_null
              - name: quarter
                description: Revenue quarter number.
              - name: gross_revenue
                description: Sum of gross order value before discounts and refunds.
                tests:
                  - dbt_expectations.expect_column_values_to_be_between:
                      min_value: 0
                      max_value: 50000
              - name: total_discounts
                description: Total order-level discounts applied in the month.
              - name: net_revenue
                description: Revenue after discounts and before refunds.
              - name: refund_amount
                description: Value of orders that were refunded in the month.
              - name: net_revenue_after_refunds
                description: Net recognized revenue after discounts and refunds.
                tests:
                  - dbt_expectations.expect_column_values_to_be_between:
                      min_value: 0
                      max_value: 50000
              - name: order_count
                description: Number of non-cancelled orders contributing to the month.
              - name: avg_order_value
                description: Average recognized order value.
              - name: mom_growth_pct
                description: Month-over-month growth percentage in recognized net revenue.

          - name: mart_vendor_performance
            description: Vendor performance mart used to rank suppliers by GMV, commissions, ratings, and return rate.
            columns:
              - name: vendor_id
                description: Vendor identifier.
                tests:
                  - not_null
                  - unique
                  - relationships:
                      to: ref('stg_vendors')
                      field: vendor_id
              - name: vendor_name
                description: Vendor display name.
              - name: vendor_category
                description: Vendor category.
              - name: vendor_status
                description: Current operational status of the vendor.
              - name: avg_rating
                description: Average vendor rating across orders.
              - name: gmv
                description: Gross merchandise value attributed to the vendor.
                tests:
                  - dbt_expectations.expect_column_values_to_be_between:
                      min_value: 0
                      max_value: 100000
              - name: vendor_revenue
                description: Recognized commission revenue from the vendor.
              - name: order_count
                description: Number of non-cancelled orders linked to the vendor.
              - name: return_rate
                description: Share of vendor orders that were refunded.
              - name: gmv_rank
                description: Dense rank of the vendor by GMV.
              - name: underperforming
                description: Boolean flag for vendors in the bottom 20 percent of GMV.
        """,
        "models/marts/product/schema.yml": """
        version: 2

        models:
          - name: mart_funnel_analysis
            description: Funnel mart used to understand where sessions drop off by acquisition channel and device.
            tests:
              - dbt_utils.unique_combination_of_columns:
                  combination_of_columns:
                    - channel
                    - device_type
                    - step_order
            columns:
              - name: channel
                description: Acquisition channel tied to the session.
                tests:
                  - not_null
                  - accepted_values:
                      values: ['paid_search', 'organic', 'referral', 'email', 'paid_social', 'unknown']
              - name: device_type
                description: Device type tied to the session.
                tests:
                  - not_null
                  - accepted_values:
                      values: ['mobile', 'desktop']
              - name: step_order
                description: Ordered numeric representation of the funnel stage.
              - name: funnel_stage
                description: Funnel stage name.
              - name: sessions_at_step
                description: Number of sessions that reached at least this funnel stage.
              - name: drop_off_rate
                description: Share of sessions that did not advance to the next stage.
              - name: conversion_rate_to_purchase
                description: Share of sessions at this step that ultimately converted to purchase.
              - name: biggest_dropoff_step_for_channel
                description: Stage with the highest average drop-off for the channel.
              - name: biggest_dropoff_rate_for_channel
                description: Highest average drop-off rate observed across funnel steps for the channel.

          - name: mart_campaign_roi
            description: Campaign-level ROI mart summarizing media efficiency and attributed revenue.
            columns:
              - name: campaign_id
                description: Campaign identifier.
                tests:
                  - not_null
                  - unique
                  - relationships:
                      to: ref('stg_campaigns')
                      field: campaign_id
              - name: campaign_name
                description: Campaign display name.
              - name: channel
                description: Acquisition channel where the campaign ran.
                tests:
                  - accepted_values:
                      values: ['paid_search', 'organic', 'referral', 'email', 'paid_social']
              - name: target_segment
                description: Audience segment targeted by the campaign.
              - name: start_date
                description: Campaign start date.
              - name: end_date
                description: Campaign end date.
              - name: budget_eur
                description: Campaign budget in EUR.
              - name: impressions
                description: Campaign impressions.
              - name: clicks
                description: Campaign clicks.
              - name: conversions
                description: Reported conversions.
              - name: ctr
                description: Click-through rate.
              - name: cvr
                description: Conversion rate.
              - name: attributed_revenue
                description: Revenue attributed to the campaign.
              - name: roas
                description: Return on ad spend.
              - name: cost_per_conversion
                description: Cost per reported conversion.
              - name: roi_tier
                description: Bucketed ROI quality tier.
                tests:
                  - accepted_values:
                      values: ['excellent', 'good', 'poor']
              - name: high_performing
                description: Boolean flag for campaigns with ROAS above 3.
        """,
        "models/marts/crm/schema.yml": """
        version: 2

        models:
          - name: mart_customer_segments
            description: CRM mart providing a full customer profile with value, churn, and retention labels.
            columns:
              - name: customer_id
                description: Customer identifier.
                tests:
                  - not_null
                  - unique
                  - relationships:
                      to: ref('stg_customers')
                      field: customer_id
                  - dbt_expectations.expect_column_proportion_of_unique_values_to_be_between:
                      min_value: 0.99
                      max_value: 1
              - name: customer_name
                description: Customer full name.
              - name: customer_email
                description: Customer email address.
              - name: segment
                description: Commercial segment.
                tests:
                  - accepted_values:
                      values: ['premium', 'standard']
              - name: ltv_segment
                description: Lifetime value segment derived from total spend.
                tests:
                  - accepted_values:
                      values: ['high', 'mid', 'low']
              - name: churn_flag
                description: Boolean churn flag based on recency.
              - name: acquisition_channel
                description: Acquisition source.
                tests:
                  - accepted_values:
                      values: ['paid_search', 'organic', 'referral', 'email', 'paid_social', 'unknown']
              - name: city
                description: Primary customer city.
              - name: age_group
                description: Customer age band.
              - name: country
                description: Customer country.
              - name: is_premium
                description: Boolean premium flag.
              - name: total_orders
                description: Total order count for the customer.
              - name: total_spend
                description: Total realized customer spend.
                tests:
                  - dbt_expectations.expect_column_values_to_be_between:
                      min_value: 0
                      max_value: 10000
              - name: avg_order_value
                description: Average realized order value.
              - name: first_order_date
                description: First order date.
              - name: last_order_date
                description: Most recent order date.
              - name: days_since_last_order
                description: Days since the most recent order.
              - name: retention_band
                description: Retention bucket based on customer recency.
                tests:
                  - accepted_values:
                      values: ['new', 'active', 'at_risk', 'churned']

          - name: mart_cohort_retention
            description: Monthly cohort retention matrix showing customer activity after signup month.
            tests:
              - dbt_utils.unique_combination_of_columns:
                  combination_of_columns:
                    - cohort_month
                    - months_since_signup
            columns:
              - name: cohort_month
                description: First month when the customer cohort signed up.
                tests:
                  - not_null
              - name: months_since_signup
                description: Month offset from cohort start.
                tests:
                  - not_null
              - name: cohort_size
                description: Number of customers in the cohort.
              - name: retained_customers
                description: Customers in the cohort with activity in the offset month.
              - name: retention_rate
                description: Retained customer share of the original cohort.
        """,
        "tests/assert_no_negative_revenue.sql": """
        select *
        from {{ ref('mart_revenue') }}
        where net_revenue_after_refunds < 0
        """,
        "tests/assert_funnel_steps_ordered.sql": """
        with session_steps as (
            select
                session_id,
                min(funnel_step) as min_step,
                max(funnel_step) as max_step,
                count(distinct funnel_step) as distinct_steps
            from {{ ref('stg_events') }}
            where session_id <> 'unknown_session'
            group by session_id
        )

        select *
        from session_steps
        where min_step <> 1
           or max_step not between 1 and 5
           or distinct_steps <> max_step
        """,
        "analyses/churn_deep_dive.sql": """
        with customer_base as (
            select *
            from {{ ref('mart_customer_segments') }}
        ),

        city_channel_segment as (
            select
                segment,
                acquisition_channel,
                city,
                count(*) as customers,
                sum(case when churn_flag then 1 else 0 end) as churned_customers,
                avg(total_spend) as avg_total_spend,
                avg(total_orders) as avg_total_orders
            from customer_base
            group by segment, acquisition_channel, city
        ),

        ranked as (
            select
                *,
                {{ safe_divide('churned_customers', 'customers') }} as churn_rate,
                dense_rank() over (
                    order by {{ safe_divide('churned_customers', 'customers') }} desc, avg_total_spend asc
                ) as churn_risk_rank
            from city_channel_segment
        )

        select
            *,
            lag(churn_rate) over (
                partition by segment
                order by churn_risk_rank
            ) as prior_churn_rate_in_segment
        from ranked
        order by churn_risk_rank, segment, acquisition_channel, city
        """,
        "analyses/campaign_budget_efficiency.sql": """
        with campaign_perf as (
            select *
            from {{ ref('mart_campaign_roi') }}
        ),

        ranked as (
            select
                *,
                dense_rank() over (
                    order by cost_per_conversion desc nulls last, attributed_revenue asc
                ) as inefficiency_rank
            from campaign_perf
        )

        select
            campaign_id,
            campaign_name,
            channel,
            target_segment,
            budget_eur,
            conversions,
            cost_per_conversion,
            attributed_revenue,
            roas,
            roi_tier,
            inefficiency_rank
        from ranked
        order by inefficiency_rank, budget_eur desc
        """,
        "README.md": """
        # marketplace_analytics

        ## 1. The Problem
        A marketplace platform was operating with 7 raw MySQL tables, manual SQL notebooks, and no shared transformation layer. Analysts could answer one question at a time, but every revenue cut, churn check, or campaign readout had to be rebuilt from scratch.

        That made the business slow and inconsistent. There was no data documentation, no reusable logic, no tests, and no lineage showing how KPI tables were produced. Dirty records such as duplicate customers, null acquisition channels, future-dated orders, bad campaign dates, and session gaps made the situation worse.

        ## 2. What We Built
        We designed a 3-layer dbt architecture for marketplace analytics. The staging layer standardizes raw seeds into clean source-aligned views, the intermediate layer applies business logic and reusable joins, and the marts layer publishes KPI-ready tables for BI and operational reporting.

        The project deliberately handles real-world data quality issues: duplicate emails in customers, nulls in acquisition_channel and age_group, null order amounts, future-dated orders, inactive products appearing in transactions, unit-price mismatches between catalog and line items, invalid campaign dates, and missing session IDs in the clickstream funnel.

        ## 3. Architecture Diagram
        ```text
        Raw Seeds (CSV) -> [Staging: views] -> [Intermediate: ephemeral] -> [Marts: tables] -> BI Dashboard
              raw source snapshots      cleaned typed data      reusable business logic       KPI-ready outputs      Power BI / Looker / Metabase
        ```

        ## 4. How It Shapes Data
        - Staging: type casting, deduplication, null handling, boolean flags, freshness-ready source definitions.
        - Intermediate: joins, aggregations, churn logic, funnel ranking, attribution logic, CLV segmentation.
        - Marts: final KPI tables, MoM growth with window functions, cohort retention, ROAS, vendor ranking, and funnel drop-off analysis.

        ## 5. KPIs This Project Answers
        | KPI | Mart Model |
        | --- | --- |
        | Monthly and quarterly revenue trend, discount impact, refund-adjusted net revenue | `mart_revenue` |
        | GMV, commission revenue, vendor ranking, underperformance, return rate | `mart_vendor_performance` |
        | Funnel reach, conversion rate, and biggest drop-off by channel and device | `mart_funnel_analysis` |
        | Campaign budget efficiency, ROAS, and low-return spend | `mart_campaign_roi` |
        | Customer CLV, churn flag, retention band, and acquisition quality | `mart_customer_segments` |
        | Monthly cohort retention by signup month | `mart_cohort_retention` |

        ## 6. How To Run
        1. Create a virtual environment and install dependencies.
           ```bash
           python -m venv .venv
           source .venv/bin/activate
           pip install -r requirements.txt
           ```
        2. Install dbt packages.
           ```bash
           dbt deps --profiles-dir .
           ```
        3. Seed the raw data into DuckDB and build the project locally.
           ```bash
           dbt seed --target dev --profiles-dir .
           dbt build --target dev --profiles-dir .
           dbt docs generate --target dev --profiles-dir .
           ```
        4. Run source freshness checks when you want operational validation.
           ```bash
           dbt source freshness --target dev --profiles-dir .
           ```
        5. Deploy to BigQuery staging with a service account secret in CI/CD.
           ```bash
           export DBT_GCP_PROJECT=your-gcp-project
           export DBT_GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account", ...}'
           dbt seed --target staging_env --profiles-dir .
           dbt build --target staging_env --profiles-dir .
           ```
        6. Run against production BigQuery from a local authenticated workstation.
           ```bash
           export DBT_GCP_PROD_PROJECT=your-prod-project
           dbt build --target prod --profiles-dir .
           ```

        ## 7. Tech Stack
        - `dbt-core`: the transformation framework that structures the project into staging, intermediate, and mart layers.
        - `DuckDB`: local developer warehouse for fast, zero-credential iteration.
        - `BigQuery`: production analytics warehouse in the EU region for scalable execution.
        - `GCP`: cloud platform for project hosting, IAM, and warehouse operations.
        - `Docker`: portable local runtime for consistent dbt execution across machines.
        - `CI/CD`: GitHub Actions pipeline that runs seeds and builds in local and staging targets.
        - `Git`: version control for SQL logic, documentation, and data model changes.
        - `dbt-utils`: shared macros and generic tests for date spines, unique combinations, and utility helpers.
        - `dbt-expectations`: expectation-style data quality tests for ranges, uniqueness ratios, and KPI sanity checks.

        ## 8. What's Next
        - Add Airflow orchestration for scheduled source freshness, seeds, builds, and downstream notifications.
        - Deploy the project in dbt Cloud with environment-level jobs and PR-aware slim CI.
        - Publish a Metabase dashboard on top of the mart layer for finance, CRM, and acquisition monitoring.
        """,
    }


def main() -> None:
    vendors = build_vendors()
    products = build_products(vendors)
    customers = build_customers()
    orders, order_items = build_orders_and_items(customers, vendors, products)
    campaigns = build_campaigns()
    events = build_events(customers, products)

    write_csv(
        "seeds/vendors.csv",
        [
            "vendor_id",
            "vendor_name",
            "category",
            "city",
            "commission_rate",
            "onboarded_date",
            "status",
            "rating",
            "loaded_at",
        ],
        vendors,
    )
    write_csv(
        "seeds/products.csv",
        [
            "product_id",
            "vendor_id",
            "product_name",
            "category",
            "base_price",
            "stock_quantity",
            "is_active",
            "created_at",
            "loaded_at",
        ],
        products,
    )
    write_csv(
        "seeds/customers.csv",
        [
            "customer_id",
            "name",
            "email",
            "city",
            "signup_date",
            "acquisition_channel",
            "segment",
            "age_group",
            "country",
            "loaded_at",
        ],
        customers,
    )
    write_csv(
        "seeds/orders.csv",
        [
            "order_id",
            "customer_id",
            "vendor_id",
            "order_date",
            "status",
            "total_amount",
            "discount_amount",
            "payment_method",
            "delivery_city",
            "loaded_at",
        ],
        orders,
    )
    write_csv(
        "seeds/order_items.csv",
        [
            "item_id",
            "order_id",
            "product_id",
            "quantity",
            "unit_price",
            "discount_pct",
            "loaded_at",
        ],
        order_items,
    )
    write_csv(
        "seeds/campaigns.csv",
        [
            "campaign_id",
            "campaign_name",
            "channel",
            "start_date",
            "end_date",
            "budget_eur",
            "impressions",
            "clicks",
            "conversions",
            "target_segment",
            "loaded_at",
        ],
        campaigns,
    )
    write_csv(
        "seeds/events.csv",
        [
            "event_id",
            "customer_id",
            "session_id",
            "event_type",
            "event_timestamp",
            "page_url",
            "device_type",
            "loaded_at",
        ],
        events,
    )

    for relative_path, content in build_static_files().items():
        write_text(relative_path, content)

    write_text("warehouse/.gitkeep", "")

    print("Generated marketplace_analytics dbt project assets.")
    print(f"customers={len(customers)} orders={len(orders)} order_items={len(order_items)} vendors={len(vendors)} products={len(products)} campaigns={len(campaigns)} events={len(events)}")


if __name__ == "__main__":
    main()
