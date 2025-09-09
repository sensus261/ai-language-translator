# 🌐 DROPSHIPPING MANAGER

**📖 View documentation in other languages:**

- [🇺🇸 English](./README.md) _(current version)_
- [🇷🇴 Română](./docs/ro/README.md)

**📋 Additional Documentation:**

- [🏗️ Architecture Documentation](./docs/en/architecture.md)
- [🚀 Development Guide](./docs/en/development-guide.md)
- [⚡ Quick Install Guide](./docs/en/project_install_quick_notes.md)

<br>
<br>

[![main-api-service](https://github.com/sensus261/dropshipping-manager/actions/workflows/main-api-service.yml/badge.svg)](https://github.com/sensus261/dropshipping-manager/actions/workflows/main-api-service.yml)

Welcome to the **DROPSHIPPING MANAGER** repository!

### ⚠️ This project was made and intended to be used on UBUNTU systems with an AMD GPU card (7900XT in this case) with AMD drivers (with ROCM) installed on the host.

### ⚠️ Minimum recommended (tested) specs: `UBUNTU / R5 3600X / 7900XT / 32GB RAM`

### ⚠️ If you want to run this on a mac-OS, you need to install the `ollama` on the host machine (because it will communicate a lot more better with your system resources) and then modify the `.env` file `OLLAMA_SERVICE_URL=http://host.docker.internal:11434` (11434 is the host ollama port). Btw prepare your RAM cuz you will need them

> For full requirements / install guide, please refer to [PROJECT INSTALL QUICK NOTES](./docs/en/project_install_quick_notes.md) and [DEVELOPMENT GUIDE](./docs/en/development-guide.md)

<br />
<br />

# Overview

## ⚙️ Services

1. **MAIN-API-SERVICE** `🛒`

   - **Tech Stack:** Laravel, Redis, Temporal, DomPDF, Excel, PostgreSQL and Filament
   - **Purpose:** Responsible for main platform logics.
   - **Links:**

   | Page            | URL                                |
   | --------------- | ---------------------------------- |
   | Admin dashboard | http://localhost:8001/admin        |
   | Log viewer      | http://localhost:8001/log-viewer   |
   | Up              | http://localhost:8001/up           |
   | Health          | http://localhost:8001/health?fresh |
   | Temporal        | http://localhost:8233              |
   | Mailcatcher     | http://localhost:1080              |
   | Redis insight   | http://localhost:5540              |
   | PGAdmin         | http://localhost:8888              |

   <br />
   <br />

2. **OLLAMA-API-SERVICE** `🛒`

   - **Tech Stack:** Python, OLLAMA SDK
   - **Purpose:** Responsible for exposing a custom API for communicating with the AI service
   - **Mentions:** A ollama instance url must be set in the `.env` -> `OLLAMA_SERVICE_URL`. It can be hosted on the host / docker machine or be external
   - **Links:**

   | Page                              | URL                   |
   | --------------------------------- | --------------------- |
   | API (`/enhance-product` - `POST`) | http://localhost:5001 |

<br />
<br />

<br />
<br />

# The Idea

### Platform Responsibilities

#### 📦 Product Management

- **Supplier products catalogue retrieval:** Automated retrieval of import files from supported suppliers containing comprehensive product data including pricing, inventory levels, and specifications
- **Supplier products catalogue ingestion:** Advanced parsing and ingestion of import files with data validation, duplicate detection, and automated product creation in the database
- **Product enhancements:** AI-powered enhancement of supplier product data including SEO-optimized descriptions, category classification, and metadata enrichment

#### 📊 Financial Management

- **Invoicing capabilities & document generations:** Comprehensive invoice management with ANAF integration for e-Factura compliance, automated import of bank transactions from Banca Transilvania, and generation of essential accounting documents including company registers and journals
- **Inventory management system:** Sophisticated inventory tracking that creates verifiable inventory items from invoices and bank transactions. Each item serves as proof of purchase and qualifies as a deductible business expense, optimizing tax efficiency and reducing overall tax liability
- **VAT balance checkups:** Advanced VAT calculation engine that processes invoices and transactions with their respective VAT rates, categorizing them as collected or paid. Generates comprehensive VAT journals for monthly or quarterly periods, calculating exact VAT balances due to tax authorities

#### 🔗 Third-Party Integrations

- **ANAF integrated:** Complete integration with Romania's National Agency for Fiscal Administration (ANAF) ensuring full e-Factura compliance and automated tax reporting
- **BT integrated:** Seamless integration with Banca Transilvania for real-time bank account monitoring and automated transaction data synchronization

#### 📈 Analytics & Reporting

- **Statistics:** Comprehensive dashboard displaying key performance indicators, financial metrics, and operational statistics based on platform settings, invoice data, transaction history, and inventory configurations with customizable reporting periods

#### 💾 Backup Management

- **Automated backup system:** Comprehensive backup functionality for the main API service including database and Laravel storage data, accessible through both the `main.sh` script and the Filament admin dashboard
- **Backup operations:** Create full backups of the main API service (database + Laravel storage), restore from existing backups, list all available backups, and clear old backups to manage storage space
- **Admin dashboard integration:** Complete backup management interface within the Filament admin dashboard allowing administrators to create, list, and restore backups directly from the web interface

<br />
<br />

# The job of the company administrator

The **Company Administrator** plays a crucial role in overseeing the platform's overall operations and ensuring optimal business performance. Their responsibilities include:

## 📊 Strategic Management

- **Platform Configuration:** Configure and maintain critical business settings, including tax rates, VAT configurations, depreciation thresholds, and accounting periods
- **User Management:** Create and manage user accounts for different roles (accountants) with appropriate permissions and access levels
- **Business Intelligence:** Monitor key performance indicators through comprehensive dashboards showing financial metrics, invoice volumes, and operational statistics

## 🔧 System Administration

- **Service Monitoring:** Oversee the health and performance of all platform services including the main API, AI enhancement services, and database systems
- **Backup Management:** Execute, schedule, and restore system backups through both the admin dashboard and command-line tools
- **Integration Oversight:** Manage and monitor third-party integrations with ANAF (Romanian tax authority) and Banca Transilvania

## 📈 Operational Excellence

- **Workflow Orchestration:** Supervise Temporal workflows for automated invoice synchronization, data processing, and system maintenance tasks
- **Quality Assurance:** Review and validate automated AI-enhanced product descriptions and ensure data integrity across all business processes
- **Compliance Management:** Ensure platform adherence to Romanian tax regulations, e-Factura requirements, and business accounting standards

## 🚨 Problem Resolution

- **Data Validation:** Oversee invoice processing, inventory management accuracy, and financial data reconciliation
- **Performance Optimization:** Identify bottlenecks, optimize system performance, and implement improvements to business workflows

<br />
<br />

# The job of the company accountant

The **Company Accountant** is responsible for maintaining accurate financial records and ensuring regulatory compliance. Their core duties within the platform include:

## 📋 Financial Record Management

- **Invoice Processing:** Review, validate, and categorize both ANAF-synchronized invoices and manually created invoices for accuracy and completeness
- **Transaction Reconciliation:** Monitor and reconcile automated bank transaction imports from Banca Transilvania with corresponding invoices and business activities
- **Inventory Accounting:** Convert invoice data into verifiable inventory items, ensuring each purchase is properly documented for tax deductibility purposes

## 🧮 Tax Compliance & Reporting

- **VAT Management:** Calculate and verify VAT balances using the platform's advanced VAT engine, ensuring accurate monthly/quarterly tax submissions
- **Document Generation:** Create essential accounting documents including company registers, VAT journals, and compliance reports for tax authorities

## 💰 Financial Analysis & Control

- **Expense Optimization:** Leverage the inventory management system to maximize tax-deductible business expenses and reduce overall tax liability
- **Cash Flow Monitoring:** Track income and expenses through integrated dashboards showing real-time financial health and business performance metrics
- **Audit Preparation:** Maintain organized digital records with complete audit trails for all financial transactions and supporting documentation

## 🔍 Verification & Quality Control

- **Data Accuracy:** Verify automated invoice data extraction and AI-enhanced categorization to ensure proper accounting treatment
- **Compliance Monitoring:** Review system-generated alerts for potential compliance issues, missing documentation, or processing errors
- **Reporting Oversight:** Generate and review financial reports, ensuring accuracy in all accounting calculations and regulatory submissions

<br />
<br />

# Getting started

## ⌛ GIT HOOKS

- To ensure that we have the git properly configured we need to install the git hooks (only pre-commit at the moment)
- We do that by running the following command (assuming we are in the root of the project):

```
./infrastructure/git/install.sh
```

- You should receive an output like this:

```
Pre-commit hook added successfully
```

- Or if the hook has been previously installed, it will be replaced by the latest version and you should receive a confirmation output like this:

```
Pre-commit hook already exists. Deleting old hook...
Pre-commit hook added successfully
```

- ✅ Congratulations! Now the git hooks are now installed.

- ❌ If for some reason (and NOT RECOMMENDED) you need to bypass the hooks, you can run your command with `--no-verify` flag. For example:

```
git commit -m "feat(api): Implemented that" --no-verify
```

<br />
<br />

## 🚀 INSTALLING THE PROJECT

- Make sure all your `.env` variables are setup correctly.

- Then run the intialize project script (this project is available only on DEBIAN distros or DARWIN)

```
./infrastructure/scripts/initialize-project.sh
```

- Or if you want to explore all the available scripts for this project, run:

```
./infrastructure/scripts/main.sh
```

- For a full guide, please refer to [PROJECT INSTALL QUICK NOTES](./docs/en/project_install_quick_notes.md)

<br>
<br>

## Steps to start the project in local mode

- Make sure the `MAIN_API_PROXY_DOMAIN` is commented in both `.env` and `services/main-api-service/.env`
- Also make sure that the docker container `main-api-https-proxy` is stoppend and NOT running
- Just use the `main.sh` script.. it will ask you when you start / initialize the project..

<br>
<br>

## Steps to start the project in public mode

- Make sure the `MAIN_API_PROXY_DOMAIN` is set in both `.env` and `services/main-api-service/.env`. This domain needs to point to your public ip. If you're behind a router with DHCP, make sure you port forward your main-api ports
- Also make sure that the SSL certificates are mapped and present in `infrastructure/nginx/certs`
- Also make sure that the docker container `main-api-https-proxy` is up and running
- Just use the `main.sh` script.. it will ask you when you start / initialize the project..
