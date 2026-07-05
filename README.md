<!-- 1) BANNER -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:7C5CFF,100:B69CFF&height=170&section=header&text=order-management-gui&fontColor=ffffff&fontSize=44&desc=Desktop%20order%20management%20over%20MySQL&descAlignY=62&descSize=16&animation=fadeIn" width="100%"/>
</p>

<!-- 2) TYPING SVG -->
<p align="center">
  <a href="https://github.com/dyntr">
    <img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&size=18&pause=1000&color=7C5CFF&center=true&vCenter=true&width=680&lines=Tkinter+GUI+over+a+MySQL+backend;Transactional+checkout+with+automatic+rollback" alt="typing"/>
  </a>
</p>

<!-- 3) BADGES -->
<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Tkinter-3776AB?style=flat-square"/>
  <img src="https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white"/>
  <img src="https://img.shields.io/badge/pandas-150458?style=flat-square&logo=pandas&logoColor=white"/>
  <img src="https://img.shields.io/badge/PyInstaller-322a7d?style=flat-square"/>
  <img src="https://img.shields.io/badge/status-school%20project-6e7681?style=flat-square"/>
</p>

## Overview

**THÉTA** is a desktop order-management application: a Tkinter GUI over a MySQL database of users, products, categories, orders and order details. It was built as a larger "ročníková práce" school project to practice relational schema design end-to-end — from the `CREATE TABLE` script to a working transactional checkout in a real GUI.

## ✦ Features

- **Login / registration** with SHA-256 password hashing (`hashlib`) and an account status check (`Aktivní` / `Neaktivní` / `Pozastaveno`) — inactive accounts can't log in.
- **Tabbed GUI** (`ttk.Notebook`) covering the whole workflow: bulk **import** (CSV/JSON/XML, with automatic `Category` → `CategoryID` lookup), manual **insert**, a generic **CRUD table manager** (search + sort on any table), **order creation**, a simpler **sale** flow (stock deduction only), a **data view**, and **reports**.
- **Transactional order creation** — placing an order inserts into `Orders` and `OrderDetails` and decrements `Products.Stock` in one commit; if stock is insufficient or any step fails, the whole transaction rolls back and nothing is written.
- **Reports** read from an `OrderSummary` SQL view (order totals per user) and export to CSV.
- **Active Record–style models** (`User`, `Order`, `OrderDetail` in `models.py`) sitting on top of small `fetch_all` / `execute_query` helpers (`db_operations.py`) — a pattern picked deliberately after comparing Active Record vs. Row Data Gateway.
- Optional **PyInstaller** build into a standalone `.exe`.

## 🛠 Built with

Python 3.9+, Tkinter, `mysql-connector-python`, `pandas` (CSV/JSON import), `pyinstaller` (optional packaging).

## 🧭 Data model

```mermaid
erDiagram
    USERS ||--o{ ORDERS : places
    CATEGORIES ||--o{ PRODUCTS : groups
    ORDERS ||--o{ ORDERDETAILS : contains
    PRODUCTS ||--o{ ORDERDETAILS : "ordered as"

    USERS {
        int UserID PK
        varchar Username
        varchar PasswordHash
        varchar Email
        enum IsActive
        datetime CreatedAt
    }
    CATEGORIES {
        int CategoryID PK
        varchar Name
        varchar Description
    }
    PRODUCTS {
        int ProductID PK
        varchar ProductName
        float Price
        int Stock
        int CategoryID FK
    }
    ORDERS {
        int OrderID PK
        int UserID FK
        datetime OrderDate
        float TotalAmount
    }
    ORDERDETAILS {
        int OrderDetailID PK
        int OrderID FK
        int ProductID FK
        int Quantity
        float PricePerUnit
    }
```

## 📦 Getting started

Requires Python 3.9+ and a local MySQL server.

```bash
pip install -r requirements.txt

# create the PVDB schema, tables and the OrderSummary view
mysql -u root -p < data/MySQLdatabase.sql

# edit data/config.json with your own MySQL host / user / password
```

Then launch the app **as a module from the project root** — the code imports itself as `src.*`, so `python src/main.py` (as the project's own original docs suggested) actually throws `ModuleNotFoundError`; the verified working command is:

```bash
python3 -m src.main
```

## 🎓 What I learned

Designing a normalized schema with foreign keys and a reporting view, wrapping multi-table writes in real commit/rollback transactions with `mysql-connector-python`, comparing the Active Record and Row Data Gateway patterns before picking one, and building a multi-tab desktop UI in Tkinter.

## 🚀 Status

Built during studies at SPŠE Ječná — a school project demonstrating database-backed desktop application design, not a deployed point-of-sale system.

<!-- FOOTER -->
---
<p align="center">
  <sub>Part of <a href="https://github.com/dyntr">Patrick Dyntr's</a> portfolio · Built by <a href="https://github.com/dyntr">@dyntr</a></sub>
</p>
