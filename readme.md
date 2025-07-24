# Vaccine - SQL Injection Detection Tool

**Vaccine** is a command-line tool for detecting SQL injection vulnerabilities in web applications. It automates the process of testing URLs for various types of SQL Injection flaws, helping developers and security professionals pinpoint and mitigate risks in their systems. Vaccine offers a comprehensive suite of tests, including time-based, error-based, and union-based injections, and can identify the underlying database engine. If a vulnerability is found, Vaccine can extract valuable information such as vulnerable parameters, database names, table names, column names, and (planned) perform a complete database dump.


![STOLEN_TABLE](https://github.com/ftTower/ftTower/blob/main/assets/Vaccine/stolen_table.png)

## Table of Contents

1. [Features](#features)
2. [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage](#usage)
5. [How it Works](#how-it-works)
6. [Makefile Commands](#makefile-commands)
7. [Sources](#sources)
8. [Disclaimer](#disclaimer)

---

## Features

- **Comprehensive Vulnerability Detection**: Identifies SQL Injection vulnerabilities using multiple techniques.
    - Union-Based Injection
    - Error-Based Injection
    - Time-Based Injection
    - Boolean-Based Injection (for POST requests)
- **Database Engine Identification**: Automatically detects the database engine (MySQL, PostgreSQL, SQL Server, Oracle, SQLite) to tailor injection attempts.
- **Detailed Vulnerability Reporting**:
    - Vulnerable parameters and payloads used
    - Database names
    - Table names
    - Column names
    - Complete database dump *(planned)*
- **Flexible Request Methods**: Supports both GET and POST HTTP request methods.
- **Persistent Storage**: Automatically stores scan results in a designated output file, creating it if it doesn't exist.
- **Command-Line Options**: Provides convenient command-line arguments for customizing scans.
- **HTTP Method Support**: Supports both GET and POST requests.
- **Data Storage**: Stores scan results in a specified or default archive file.

---

## Getting Started

### Prerequisites

- Python 3.x
- `pip` (Python package installer)
- `make` (for Makefile commands)
- Docker (for setting up the SQLi-Labs environment)
- Required Python libraries: `requests`, `selenium`, `urllib.parse`

### Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/vaccine.git
    cd vaccine
    ```

2. **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **(Optional) Setup SQLi-Labs for Testing:**
    This project includes a Makefile target to set up a local SQLi-Labs environment using Docker for safe, legal testing.
    ```bash
    make labs
    ```
    The get lab will be accessible at [http://localhost:1338/](http://localhost:1338/).
    The post lab will be accessible at [http://localhost:1338/](http://localhost:8080/).

---

## Configuration

By default, scan results are stored in a default file unless the `-o` option is specified. You can configure this file in `utils/utils.py` or `core/main.py` if needed.

---

## Usage

Run Vaccine from the command line:

```bash
./vaccine [-o <archive_file>] [-X <request_type>] URL
```

**Options:**
- `-o <archive_file>`: Output file for scan results (default: `results.json`)
- `-X <request_type>`: HTTP method (`GET` or `POST`, default: `GET`)

**Examples:**


- Basic GET request scan:
    ```bash
    ./vaccine http://localhost:1338/
    ```
![GET](https://github.com/ftTower/ftTower/blob/main/assets/Vaccine/get_interface.png)

- Scan with POST method and custom output file:
    ```bash
    ./vaccine -X POST -o my_scan_results.json http://localhost:1338/
    ```
![POST](https://github.com/ftTower/ftTower/blob/main/assets/Vaccine/post_interface.png)


---

## How it Works

![UNION_PAYLOAD](https://github.com/ftTower/ftTower/blob/main/assets/Vaccine/payloads.png)


1. **Crawling**: Performs a simple crawl to identify potential entry points or parameters within the provided URL.
2. **Database Detection**: Identifies the underlying database engine by sending specific payloads and analyzing server responses (e.g., error messages, time delays).
3. **Injection Attempts**:
    - **GET Requests**: Iterates through identified parameters in the URL and attempts various SQL Injection techniques (e.g., UNION SELECT, error-based payloads, time-based delays).
    - **POST Requests**: Parses forms on the target page, injects payloads into input fields, and analyzes the responses. Boolean-based injection is primarily used for POST.
4. **Result Analysis**: Determines if a vulnerability exists based on server behavior (e.g., error messages, response times, content differences).
5. **Data Extraction**: Extracts valuable information such as database version, schema, table names, and column names for vulnerable sites.

---

## Makefile Commands

- `make labs`: Set up SQLi-Labs Docker environment
- `make clean_labs`: Tear down SQLi-Labs Docker environment
- `make run`: Run the main script with a predefined URL
- `make clean`: Remove Python bytecode and `__pycache__`
- `make fclean`: Clean project and labs
- `make re`: Rebuild and restart everything

---

## SOURCES
- [to know](https://www.vaadata.com/blog/fr/injections-sql-principes-impacts-exploitations-bonnes-pratiques-securite/)
- [video about sql](https://www.vaadata.com/blog/fr/injections-sql-principes-impacts-exploitations-bonnes-pratiques-securite/)
- [tutorial](https://www.linuxsec.org/2014/03/tutorial-basic-sql-injection.html)
- [request](https://realpython.com/python-requests/#getting-started-with-pythons-requests-library)
- [beautifulSoup](https://www.scraperapi.com/blog/python-beautifulsoup-find-and-findall-methods/)

---

## Disclaimer

**For educational and authorized penetration testing only.**  
Do not use this tool on systems without explicit permission. Unauthorized testing is illegal and unethical. The authors are not responsible for misuse or damage caused by this tool.

