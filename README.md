# Restaurant Database Management System

A complete database application for managing a full-service restaurant, built with Python and SQLite.

**Course:** CSC 4402 - Database Systems  

**Project:** Fall 2025 Database Project

**Authors:** Alexis Harvey, Aaroh Desai, and Sean Pham

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Database Schema](#database-schema)
4. [Requirements](#requirements)
5. [Installation](#installation)
6. [Database Setup](#database-setup)
7. [CLI Commands](#cli-commands)
8. [Test Queries](#test-queries)
9. [Project Structure](#project-structure)

---

## Overview

This system manages all aspects of a mid-sized restaurant including:

- **Customer Management** - Track customer information and order history
- **Employee Management** - Staff roles, schedules, and supervision hierarchy
- **Table Management** - Seating capacity and locations
- **Reservation System** - Book tables for specific dates and times
- **Menu Management** - Items organized by categories with pricing
- **Order Processing** - Track orders with items, totals, and tips
- **Shift Scheduling** - Employee work schedules

---

## Features

- **SQLite Database** - Lightweight, serverless database
- **Faker Data Generation** - Realistic synthetic data for testing
- **Typer CLI** - Modern command-line interface with rich formatting
- **Role-Based Commands** - Separate commands for hosts, servers, and managers
- **Comprehensive Queries** - Pre-built reports and analytics

---

## Database Schema

### Entity-Relationship Summary

```
CUSTOMERS ──────< RESERVATIONS >────── TABLES
                      │
                      │
EMPLOYEES ─────< SHIFTS
    │
    └──────────< ORDERS >──────< ORDER_ITEMS >────── MENU_ITEMS ──────> CATEGORIES
                                                          
EMPLOYEES (self-referential: manager_id)
```

### Tables

| Table | Description |
|-------|-------------|
| `customers` | Restaurant patrons with contact information |
| `employees` | Staff members with roles, wages, and manager relationships |
| `tables` | Physical tables with capacity and location |
| `categories` | Menu organization (Appetizers, Entrees, etc.) |
| `menu_items` | Food and drink items with prices |
| `reservations` | Customer bookings for specific tables/times |
| `shifts` | Employee work schedules |
| `orders` | Customer orders with totals and status |
| `order_items` | Individual items within orders (weak entity) |


---

## Requirements

- **Python 3.8+**
- **pip** (Python package manager)

### Dependencies

```
faker>=18.0.0    # Synthetic data generation
typer>=0.9.0     # CLI framework
rich>=13.0.0     # Terminal formatting
```

Note: `sqlite3` is included in Python's standard library.

---

## Installation

### 1. Clone or Download the Project

```bash
cd "/Users/alexisharvey/Desktop/4402/DATABASE PROJECT"
```

### 2. Create a Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
.\venv\Scripts\activate   # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Database Setup

### Initialize the Database

Create the database schema:

```bash
python cli.py init
```

### Initialize and Seed with Sample Data

Create schema and populate with realistic sample data:

```bash
python cli.py init --seed
```

Or seed separately:

```bash
python cli.py seed
```

### Check Database Status

```bash
python cli.py status
```

**Example Output:**
```
┌─────────────┬──────────────┐
│ Table       │ Record Count │
├─────────────┼──────────────┤
│ customers   │           50 │
│ employees   │           20 │
│ tables      │           18 │
│ categories  │            6 │
│ menu_items  │           47 │
│ reservations│           65 │
│ shifts      │          420 │
│ orders      │          150 │
│ order_items │          595 │
└─────────────┴──────────────┘
```

---

## CLI Commands

### General Commands

```bash
# Show all available commands
python cli.py --help

# Initialize database
python cli.py init

# Initialize with sample data
python cli.py init --seed

# Seed existing database
python cli.py seed

# Check database status
python cli.py status
```

---

### Host Commands

Commands for managing reservations and tables.

#### View Available Tables

```bash
python cli.py host tables 2025-12-01 18:00
```

**Example Output:**
```
┌──────────────────────────────────────────┐
│ Available Tables - 2025-12-01 at 18:00   │
├──────────┬──────────┬────────────────────┤
│ Table #  │ Capacity │ Location           │
├──────────┼──────────┼────────────────────┤
│ T01      │    2     │ Main Dining        │
│ T03      │    4     │ Main Dining        │
│ T12      │    2     │ Patio              │
│ T17      │   12     │ Private Room       │
└──────────┴──────────┴────────────────────┘
```

#### Create a Reservation

```bash
python cli.py host reservation \
    --customer 5 \
    --table 3 \
    --date 2025-12-15 \
    --time 19:00 \
    --party 4 \
    --notes "Anniversary dinner"
```

**Example Output:**
```
╭─────────────────────────────────╮
│ ✓ New Reservation               │
├─────────────────────────────────┤
│ Reservation created successfully│
│                                 │
│ Reservation ID: 78              │
│ Customer: John Smith            │
│ Table: T03                      │
│ Date: 2025-12-15 at 19:00       │
│ Party Size: 4                   │
╰─────────────────────────────────╯
```

#### List Upcoming Reservations

```bash
# All upcoming reservations
python cli.py host reservations

# Filter by date
python cli.py host reservations --date 2025-12-01
```

---

### Server Commands

Commands for managing orders.

#### View Menu

```bash
# Full menu
python cli.py server menu

# Filter by category
python cli.py server menu --category Entrees
```

**Example Output:**
```
┌────────────────────────────────────────────┐
│ Entrees                                    │
├──────┬─────────────────────┬───────┬───────┤
│ ID   │ Item                │ Price │ Avail │
├──────┼─────────────────────┼───────┼───────┤
│ 15   │ Grilled Salmon      │ $28.99│   ✓   │
│ 16   │ Filet Mignon        │ $42.99│   ✓   │
│ 17   │ New York Strip      │ $38.99│   ✓   │
│ ...  │ ...                 │ ...   │  ...  │
└──────┴─────────────────────┴───────┴───────┘
```

#### Create a New Order

```bash
python cli.py server order \
    --server 5 \
    --table 3 \
    --customer 10 \
    --type Dine-In
```

**Example Output:**
```
╭─────────────────────────────────╮
│ ✓ New Order                     │
├─────────────────────────────────┤
│ Order created successfully!     │
│                                 │
│ Order ID: 156                   │
│ Server: Jane Doe                │
│ Type: Dine-In                   │
│ Status: Open                    │
╰─────────────────────────────────╯
```

#### Add Items to an Order

```bash
python cli.py server add-item \
    --order 156 \
    --item 16 \
    --qty 2 \
    --notes "Medium rare"
```

**Example Output:**
```
╭─────────────────────────────────╮
│ ✓ Item Added                    │
├─────────────────────────────────┤
│ Item: Filet Mignon              │
│ Quantity: 2                     │
│ Unit Price: $42.99              │
│ Item Total: $85.98              │
│                                 │
│ New Order Total: $93.07         │
╰─────────────────────────────────╯
```

---

### Manager Commands

Commands for reports and menu management.

#### Sales Reports

```bash
# Daily revenue (last 30 days)
python cli.py manager report --type daily

# Revenue by category
python cli.py manager report --type category

# Revenue by server
python cli.py manager report --type server

# Daily report for specific period
python cli.py manager report --type daily --days 7
```

**Example Output (Daily):**
```
┌─────────────────────────────────────────────────────────────┐
│ Daily Revenue Report (Last 30 Days)                         │
├────────────┬────────┬──────────┬────────┬────────┬──────────┤
│ Date       │ Orders │ Subtotal │ Tax    │ Tips   │ Total    │
├────────────┼────────┼──────────┼────────┼────────┼──────────┤
│ 2025-11-25 │      5 │  $342.50 │ $28.26 │ $54.80 │  $425.56 │
│ 2025-11-24 │      8 │  $567.80 │ $46.84 │ $85.17 │  $699.81 │
│ ...        │    ... │      ... │    ... │    ... │      ... │
└────────────┴────────┴──────────┴────────┴────────┴──────────┘

Total Revenue: $12,456.78
```

#### Add a New Menu Item

```bash
python cli.py manager menu-add \
    --name "Truffle Risotto" \
    --price 26.99 \
    --category 3 \
    --desc "Arborio rice with black truffle and parmesan"
```

#### Update Menu Item

```bash
# Update price
python cli.py manager menu-update --id 15 --price 31.99

# Mark as unavailable
python cli.py manager menu-update --id 20 --available false

# Update description
python cli.py manager menu-update --id 15 --desc "Fresh Atlantic salmon, pan-seared"
```

#### View Employees

```bash
python cli.py manager employees
```

#### View Popular Items

```bash
python cli.py manager popular --limit 10
```

#### View Top Customers

```bash
python cli.py manager customers --limit 10
```

---

## Test Queries

### Running Test Queries in Python

```bash
python queries.py
```

This executes all five required test queries and displays formatted results.

### Running SQL Queries Directly

```bash
sqlite3 restaurant.db < queries.sql
```

Or interactively:

```bash
sqlite3 restaurant.db
sqlite> .read queries.sql
```

### The Five Test Queries

1. **Revenue by Server** - Joins orders, order_items, menu_items, and employees to calculate total revenue per server

2. **Popular Menu Items** - Counts how many times each item appears in orders, grouped and sorted by count

3. **Above-Average Customers** - Uses subquery to find customers who spent more than average

4. **Overbooked Reservations** - Finds reservations where party size exceeds table capacity

5. **Category Price Update** - Updates all prices in a category by a percentage

### Query Examples

```python
from queries import (
    get_revenue_by_server,
    get_popular_menu_items,
    get_above_average_customers,
    get_overbooked_reservations,
    update_category_prices
)

# Get top 10 popular items
popular = get_popular_menu_items(10)
for item in popular:
    print(f"{item['item_name']}: {item['times_ordered']} orders")

# Find high-spending customers
vip_customers = get_above_average_customers()
for customer in vip_customers:
    print(f"{customer['customer_name']}: ${customer['total_spent']:.2f}")

# Update entree prices by 10%
updated_count = update_category_prices("Entrees", 10)
print(f"Updated {updated_count} items")
```

---

## Project Structure

```
DATABASE PROJECT/
├── README.md           
├── requirements.txt    # Python dependencies
├── schema.sql          # Database schema (DDL)
├── database.py         # Database connection utilities
├── seed_data.py        # Data generation 
├── queries.py          # Test queries in Python
├── queries.sql         # Test queries in SQL
├── cli.py              # Command-line interface
└── restaurant.db       # SQLite database (created after init)
```



