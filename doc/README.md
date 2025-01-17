# Projekt THÉTA (správa objednávek)

**Autor**: Patrick Dyntr  
**Datum**: 15. 1. 2025  
**Škola**: Střední průmyslová škola elektrotechnická, Praha 2, Ječná 30  
**Kontakt**: patrick.dyntr@gmail.com, tel: 607111006  
**Poznámka**: Jedná se o školní projekt.

---

## 1. Účel a popis aplikace

Aplikace **THÉTA** slouží ke správě objednávek, produktů, uživatelů a kategorií.  
Umožňuje:

- **Vkládat záznamy** ručně (jednotlivé položky) i hromadně (import CSV/JSON/XML).
- **Spravovat tabulky** (Users, Products, Orders, OrderDetails, Categories).
- **Vytvářet objednávky** transakčně (s odečtem skladu a zapsáním do Orders + OrderDetails).
- **Generovat reporty** s agregacemi (např. celková hodnota objednávek) a exportovat je do CSV.
- **Konfigurovat aplikaci** pomocí `config.json` (např. připojení k DB).

---

## 2. Struktura projektu

```plaintext
projekt-theta/
  ├─ src/
  │   ├─ main.py           (spouštěcí bod aplikace)
  │   ├─ db_operations.py  (připojení k DB, funkce fetch_all, execute_query)
  │   ├─ models.py         (Active Record třídy: User, Order, OrderDetail)
  │   └─ ui/
  │       ├─ app.py        (run_application funkce)
  │       ├─ main_window.py (hlavní GUI okno s Notebookem)
  │       └─ windows/
  │           ├─ login.py, register.py (okna pro přihlášení/registraci)
  │           ├─ tab_import.py, tab_insert.py, tab_manage.py, tab_order.py,
  │           ├─ tab_sale.py, tab_view.py, tab_report.py (GUI záložky)
  ├─ data/
  │   ├─ config.json       (nastavení připojení k databázi)
  │   ├─ MySQLdatabase.sql (SQL skript pro vytvoření DB a tabulek)
  │   └─ (případné .csv/.json/.xml testovací soubory)
  ├─ doc/
  │   ├─ README.txt        (tento soubor)
  │   ├─ Test1.pdf         (test case)
  │   ├─ Test2.pdf         (test case)
  │   └─ Test3.pdf         (test case)
  └─ requirements.txt      (seznam pip knihoven: mysql-connector-python, pandas...)
```

---

## 3. Instalace a spuštění

### Požadavky

- **Python 3.9+**
- **MySQL** server
- Knihovny z `requirements.txt`

### Postup

1. **Stažení projektu** (např. `projekt-theta.zip`) a rozbalení.
2. **Instalace knihoven**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Vytvoření databáze**:
   V MySQL spustit skript:
   ```sql
   source data/MySQLdatabase.sql;
   ```
   Tím se založí schéma, tabulky (Users, Products, Orders...), pohledy (OrderSummary, atd.).
4. **Konfigurace**:
   Otevřete `data/config.json` a ověřte parametry:
   ```json
   {
     "host": "127.0.0.1",
     "user": "root",
     "password": "rootroot",
     "database": "PVDB"
   }
   ```
   Případně upravte pro svou instanci MySQL.
5. **Spuštění aplikace**:
   - Windows:
     ```bash
     python src\main.py
     ```
   - macOS/Linux:
     ```bash
     python3 src/main.py
     ```
6. **(Volitelné)** Vytvoření spustitelného souboru (.exe):
   ```bash
   pip install pyinstaller
   pyinstaller --onefile src/main.py
   ```
   Vznikne `main.exe` ve složce `dist/`. Přeneste k němu `data/config.json` a další potřebné soubory.

---

## 4. Popis hlavních funkcí

### 4.1 Přihlášení / Registrace

- **Přihlášení**  
  Ověřuje se kombinace `Username` a `PasswordHash` v tabulce `Users`. Aplikace zároveň kontroluje, zda je uživatel aktivní (`IsActive = 'Aktivní'`). Pokud je stav uživatele jiný (např. „Neaktivní“), přihlášení se nezdaří.

- **Registrace**  
  Při registraci se vytvoří nový záznam v tabulce `Users`, který obsahuje zadané uživatelské jméno, zahešované heslo (`PasswordHash`), e-mailovou adresu a volitelně stav účtu (`IsActive`).

---

### 4.2 Záložky (Notebook) v GUI

1. **Import Dat**  
   - Umožňuje hromadný import z **CSV/JSON/XML** do zvolené tabulky (např. `Products`).
   - Automaticky transformuje sloupec `Category` na `CategoryID`, pokud je to potřeba (dohledáním v tabulce `Categories`).

2. **Vložit Záznam**  
   - Slouží k ručnímu vložení jednoho nového záznamu do vybrané tabulky.  
   - Uživatel vybere tabulku, vyplní formulář a odešle záznam do databáze.

3. **Správa Tabulky**  
   - Poskytuje **CRUD operace** (Create, Read, Update, Delete) pro libovolnou tabulku.  
   - Umožňuje filtraci, vyhledávání podle sloupců, případně řazení dle sloupce `CreatedAt`.

4. **Objednávka**  
   - **Transakční** vytvoření objednávky.  
   - Uživatel přidává do objednávky více položek (produkty, množství).  
   - Při potvrzení dojde k:
     1. Vložení záznamu do `Orders`,  
     2. Vložení všech položek do `OrderDetails`,  
     3. Odečtu skladu (`Stock` v tabulce `Products` se sníží o objednané množství).  
   - Pokud během procesu nastane chyba (např. **nedostatek na skladě**), proběhne **rollback** a objednávka se neuloží.

5. **Prodej**  
   - Jednoduchý **odečet skladu** bez tvorby objednávky.  
   - Po vybrání konkrétního produktu a zadání množství se odečte hodnota z `Stock` v tabulce `Products`.

6. **Zobrazit Data**  
   - Prosté zobrazení vybrané tabulky s možností:
     - **Hledání** (univerzální filtr),
     - **Řazení** dle sloupce (např. data),
     - Prohlížení záznamů v přehledné tabulce.

7. **Reporty**  
   - Pracuje s pohledem `OrderSummary`, kde jsou agregovaná data o objednávkách (OrderID, OrderDate, Username, TotalValue).  
   - Možnost **exportu do CSV**.

---

### 4.3 Transakce

Aplikace využívá **transakcí** (kombinace `commit` / `rollback`) zejména:

- Při vytváření objednávek (operace nad `Orders`, `OrderDetails`, aktualizace `Products`).
- Při **importech dat**, kde by chyba v importu mohla jinak vést k částečně vloženým nevalidním záznamům.

Pokud nastane **SQL chyba** nebo jiný problém (např. nedostatek na skladě), dojde k **rollbacku** a stav databáze se vrátí do původního stavu.

---

### 4.4 Reporty

- **OrderSummary** je pohled, který slučuje data z tabulek `Orders`, `OrderDetails` a `Users`, především kvůli výpočtu sloupce `TotalValue` = součet `(Quantity × PricePerUnit)`.
- V záložce **Reporty** lze tento souhrn zobrazit a exportovat do **CSV** (hlavičky: `OrderID;OrderDate;Username;TotalValue`).

---

## 5. Konfigurace programu

V souboru `data/config.json`:

```json
{
  "host": "127.0.0.1",
  "user": "root",
  "password": "rootroot",
  "database": "PVDB"
}
```

- **host**: IP/hostname MySQL serveru.
- **user**: MySQL uživatel.
- **password**: MySQL heslo.
- **database**: Název databáze.

Pokud se nedaří připojit, program vypíše chybu "Chyba SQL" s detailním textem.

---

## 6. Chybové hlášky a řešení

- **Nelze se připojit k MySQL**: Zkontrolujte `config.json`.
- **Nedostatek skladu**: Zvyšte `Stock` v tabulce `Products` nebo snižte množství objednávky.
- **Neexistující kategorie**: Založte odpovídající záznam v `Categories`.
- **Neplatné CSV**: Opravte formát CSV (první řádek musí obsahovat hlavičku).

---

## 7. Knihovny třetích stran

- **mysql-connector-python**: Připojení k MySQL.
- **pandas**: Práce s daty (CSV/JSON).
- **pyinstaller**: Vytváření spustitelných souborů.

---
## 8. UML Use Case diagram (přehled funkcí)

Níže je ukázka jednoduchého Use Case diagramu pro základní funkcionality **Aplikace THÉTA**:

      +------------+
      | Uživatel   |
      +------+-----+
             |
             |  (spustit aplikaci)
             v
    +-----------------------+
    | Aplikace THÉTA (GUI) |
    +---------+------------+
          |
          | 1) Přihlásit se
          | 2) Registrovat se
          | 3) Prohlížet data
          | 4) Spravovat data
          | 5) Vytvářet objednávky
          | 6) Importovat/exportovat
          v
     <Use Cases>

### UC1: Přihlášení
Uživatel zadá přihlašovací jméno a heslo, systém ověří údaje v tabulce `Users`.  
Pokud `IsActive` != `Aktivní`, přihlášení se nezdaří.

### UC2: Registrace
Uživatel vyplní registrační formulář, systém vytvoří nový záznam v tabulce `Users` (včetně `PasswordHash`, e-mailu apod.).

### UC3: Prohlížení dat
Uživatel vybere tabulku (např. `Products`, `Users`, `Orders` atd.) a prohlíží ji s možností filtrování (např. podle názvu produktu).

### UC4: Správa dat (CRUD)
Uživatel může provádět vytvoření, úpravu nebo smazání záznamu ve zvolené tabulce (např. přidat nového uživatele, upravit existující produkt).

### UC5: Vytváření objednávek
Probíhá transakčně:
- Vložení objednávky do `Orders`
- Vložení příslušných položek do `OrderDetails`
- Odečet příslušného množství produktů ze `Stock`
- Při chybě (např. nedostatek skladem) se provede rollback a objednávka se neuloží

### UC6: Import a export
- **Import**: hromadné načtení z CSV/JSON/XML do vybrané tabulky (např. `Products`)
- **Export**: zejména export reportů (pohled `OrderSummary`) do CSV souboru

---

## 9. Architektura aplikace (UML struktura)

Aplikace využívá následující hlavní komponenty:

- **GUI vrstvu (tkinter)** – okna, formuláře (moduly `src.ui.*`).
- **Model vrstvu (třídy `User`, `Order`, `OrderDetail`)** – třídy typu *Active Record*.
- **DB vrstvu (funkce `fetch_all`, `execute_query` v `db_operations.py`)** – volání MySQL.

---

### 9.1 Class diagram (zjednodušený náhled)

Níže je zjednodušený UML class diagram, zachycující vztahy mezi hlavními třídami:

    +-----------------+       +-----------------+
    | db_operations   |       | models          |
    |-----------------|       |-----------------|
    | +fetch_all(...) |<----- +User             |
    | +execute_query(...)     | +save()         |
    +-----------------+       | +delete()       |
                              | +find_by_id(...)|
                              | +find_by_username_and_password(...)
                              +-----------------+
                                   ^
                                   |
                           +-------+--------+
                           |     Order      |
                           |--------------- |
                           | +details:list  |
                           | +save()        |
                           +-------^--------+
                                   |
                          +--------+---------+
                          |   OrderDetail    |
                          +------------------+


- Třídy `User`, `Order` a `OrderDetail` volají funkce `fetch_all` a `execute_query` v modulu `db_operations.py`, aby komunikovaly s databází.
- Třída `Order` navíc obsahuje seznam `details` (objektů `OrderDetail`), což zjednodušuje společné ukládání položek objednávky v jedné transakci.

- Nejsou zde zobrazeny všechny další GUI třídy, jen logické jádro.

      ┌─────────────┐               ┌─────────────────────┐
      │ Uživatel    │               │  MySQL Server (DB)  │
      │(OS Windows) │               │  Schéma: PVDB       │
      └─────┬───────┘               └────────┬────────────┘
            │      python main.py            │
            │  (spustí tkinter GUI)          │
            v                                v
      ┌───────────────────────────┐   ┌─────────────────────────────────┐
      │ Aplikace THÉTA (Py + Tk)  │→→ │ Obslouží SQL dotazy (SELECT,...)│
      │  - main.py                │   │ - Databáze: Users, Products,... │
      │  - models.py + db_ops     │   └─────────────────────────────────┘
      └───────────────────────────┘

- **Aplikace** běží lokálně na klientském PC a obsahuje uživatelské rozhraní (tkinter).
- **MySQL server** může běžet na tomtéž počítači nebo na vzdáleném serveru. Aplikace se připojuje pomocí `mysql-connector-python`.


---

### 9.2 Deployment diagram (zjednodušený)

Zobrazuje, jak **Aplikace THÉTA** (např. spuštěná na PC s Windows) komunikuje s MySQL serverem:

---

## 10. Behaviorální diagram (Activity) – příklad „Vytvoření objednávky“

Zde je ukázka zjednodušeného **Activity diagramu**, který ilustruje postup při kliknutí na tlačítko „Vytvořit objednávku“:

    ┌───────────┐
    │Start uživ.│
    └────┬──────┘
         │
         v
    ┌───────────────────────────────┐
    │Vyplnění položek objednávky    │
    │(výběr produktů, množství...)  │
    └────┬──────────────────────────┘
         │[klik na "Vytvořit"]
         v
    ┌─────────────────────────────────────┐
    │Zahájení transakce (Order.save())    │
    └────┬────────────────────────────────┘
         │
         │(1) INSERT do tabulky Orders
         │(2) INSERT do OrderDetails
         │(3) UPDATE sklady v Products
         v
    ┌─────────────────────────────────────┐
    │Pokud dojde k chybě => rollback      │
    │jinak => commit                      │
    └────┬────────────────────────────────┘
         │
         v
    ┌───────────┐
    │Hotovo     │
    └───────────┘


> **Poznámka**: Pokud například dojde při vytvoření objednávky k nedostatku položky na skladě (`Stock`), transakce se vrátí do původního stavu (`rollback`), takže objednávka nebude zapsána.

---

## 11. E-R model databáze

V databázi **PVDB** se nachází následující tabulky:

1. **Users**  
   - **UserID** (PK)  
   - Username (VARCHAR 50)  
   - PasswordHash (VARCHAR 255)  
   - Email (VARCHAR 100)  
   - IsActive (ENUM: *Aktivní*, *Neaktivní*, *Pozastaveno*)  
   - CreatedAt (DATETIME)

2. **Categories**  
   - **CategoryID** (PK)  
   - Name (VARCHAR 100)  
   - Description (VARCHAR 255)

3. **Products**  
   - **ProductID** (PK)  
   - ProductName (VARCHAR 100)  
   - Price (FLOAT)  
   - Stock (INT)  
   - CategoryID (FK → Categories.CategoryID)

4. **Orders**  
   - **OrderID** (PK)  
   - UserID (FK → Users.UserID)  
   - OrderDate (DATETIME)  
   - TotalAmount (FLOAT)

5. **OrderDetails**  
   - **OrderDetailID** (PK)  
   - OrderID (FK → Orders.OrderID)  
   - ProductID (FK → Products.ProductID)  
   - Quantity (INT)  
   - PricePerUnit (FLOAT)

### Vztahy (relace)

- **1 : N** mezi **Users** a **Orders** (jeden uživatel může mít více objednávek).
- **1 : N** mezi **Categories** a **Products** (jedna kategorie může mít více produktů).
- **1 : N** mezi **Orders** a **OrderDetails** (jedna objednávka může obsahovat více řádků).
- **1 : N** mezi **Products** a **OrderDetails** (jeden produkt může být ve více objednávkách).

Schématicky lze relace mezi tabulkami zobrazit takto:

    Users (1) ——< Orders (1) ——< OrderDetails >—— (1) Products —— (1) Categories

---

## 12. Schéma importovaných a exportovaných souborů

### 12.1 Import (CSV/JSON/XML)

V záložce **„Import Dat“** lze hromadně vkládat data do vybraných tabulek (`Users`, `Products`, `Orders`, `OrderDetails`, `Categories`).

#### Příklad CSV pro `Users`

```csv
Username,PasswordHash,Email,IsActive
admin,d033e22ae...,admin@example.com,Aktivní
john,8c697...,john@gmail.com,Aktivní
```
- **Username**: text (max 50 znaků)  
- **PasswordHash**: hash hesla (SHA-256)  
- **Email**: nepovinný (max 100 znaků)  
- **IsActive**: 'Aktivní','Neaktivní','Pozastaveno'  

---
### Příklad CSV pro Products

```csv
ProductName,Price,Stock,Category
Čokoláda,30.50,100,Potraviny
Mýdlo,20,50,Drogerie
```

V tabulce `Products` se poté sloupec `Category` mapuje na `CategoryID` dle `Categories.Name`.  
Pokud kategorie v `Categories` neexistuje, import skončí chybou.

---

### Struktura JSON

JSON může být pole objektů:

```json
[
  {
    "Username": "jirka",
    "PasswordHash": "e3afed...5",
    "Email": "jirka@seznam.cz",
    "IsActive": "Aktivní"
  },
  {
    "Username": "eva",
    "PasswordHash": "d033e22ae...",
    "Email": "eva@example.com",
    "IsActive": "Neaktivní"
  }
]
```

---

### Struktura XML

V XML se očekává kořenový element (např. `<Users>`), v němž jsou `<row>`:

```xml
<Users>
  <row>
    <Username>admin2</Username>
    <PasswordHash>d033e22ae...</PasswordHash>
    <Email>admin2@example.com</Email>
    <IsActive>Aktivní</IsActive>
  </row>
  ...
</Users>
```

---

### Export (CSV report)

V záložce „Reporty“ lze uložit do CSV souhrn objednávek z pohledu `OrderSummary`.  
Ukázka hlavičky a řádků:

```csv
OrderID;OrderDate;Username;TotalValue
1;2025-01-15 10:05:12;admin;150.00
2;2025-01-15 11:20:45;john;89.00
```

- **OrderID**: Primární klíč objednávky  
- **OrderDate**: Datum a čas vytvoření  
- **Username**: Jméno uživatele z tabulky `Users`  
- **TotalValue**: Celková hodnota (součet) v `OrderDetails`

---

## 13. Zdroje

Níže uvádím seznam zdrojů, které jsem využil při tvorbě projektu **THÉTA**, a shrnutí toho, co jsem si z nich odnesl:

---

#### 1. **W3Schools – Python MySQL**
- [https://www.w3schools.com/python/python_mysql_getstarted.asp](https://www.w3schools.com/python/python_mysql_getstarted.asp)  
- [https://www.w3schools.com/python/python_mysql_delete.asp](https://www.w3schools.com/python/python_mysql_delete.asp)  
**Co jsem si vzal:**  
Naučil jsem se základní operace s MySQL v Pythonu pomocí knihovny `mysql-connector-python`. Tyto návody mi pomohly pochopit, jak vytvořit připojení k databázi, provádět dotazy (SELECT, INSERT, DELETE) a jak zacházet s chybami při práci s databází.

---

#### 2. **W3Schools – Python JSON**
- [https://www.w3schools.com/python/python_json.asp](https://www.w3schools.com/python/python_json.asp)  
**Co jsem si vzal:**  
Z tohoto zdroje jsem získal znalosti o práci s JSON v Pythonu. Použil jsem je při implementaci konfigurace aplikace pomocí souboru `config.json` a při načítání a ukládání dat v JSON formátu.

---

#### 3. **W3Schools – Python File Handling**
- [https://www.w3schools.com/python/python_file_handling.asp](https://www.w3schools.com/python/python_file_handling.asp)  
**Co jsem si vzal:**  
Díky tomuto návodu jsem se naučil základní operace se soubory, jako je čtení, zápis a práce s CSV a dalšími formáty. Tyto znalosti jsem použil při implementaci funkcí pro import/export dat.

---

#### 4. **Martin Fowler – Row Data Gateway Pattern**
- [https://martinfowler.com/eaaCatalog/rowDataGateway.html](https://martinfowler.com/eaaCatalog/rowDataGateway.html)  
**Co jsem si vzal:**  
Tento článek mi pomohl pochopit principy návrhového vzoru **Row Data Gateway**, který jsem částečně implementoval v rámci třídy `db_operations` (pro práci s jednotlivými řádky tabulek v databázi).

---

#### 5. **YouTube – Row Data Gateway Design Pattern Explained**
- [https://www.youtube.com/watch?v=1gkUWgJDoBc](https://www.youtube.com/watch?v=1gkUWgJDoBc)  
**Co jsem si vzal:**  
Video mi prakticky ukázalo, jak aplikovat vzor **Row Data Gateway** v kódu. Pomohlo mi zejména při návrhu metod pro manipulaci s daty v databázi, jako je vkládání a aktualizace záznamů.

---

#### 6. **StudySection – Active Record Pattern in Python**
- [https://studysection.com/blog/active-record-pattern-in-python/](https://studysection.com/blog/active-record-pattern-in-python/)  
**Co jsem si vzal:**  
Díky tomuto článku jsem se seznámil s návrhovým vzorem **Active Record**, který jsem použil v třídách `User`, `Order` a `OrderDetail`. Naučil jsem se, jak tyto třídy kombinují data a chování (např. uložení dat do databáze).

---

#### 7. **YouTube – Active Record Explained**
- [https://www.youtube.com/watch?v=ZRdgVuIppYQ](https://www.youtube.com/watch?v=ZRdgVuIppYQ)  
**Co jsem si vzal:**  
Video mi pomohlo lépe pochopit výhody a nevýhody vzoru **Active Record**. Díky tomu jsem zvolil správný přístup pro implementaci tříd, které komunikují s databází a zároveň obsahují obchodní logiku.

---

