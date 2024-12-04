# FinSailor

**FinSailor** is a comprehensive full-stack web application designed to help users track and manage investments across multiple brokers, such as Zerodha and Groww. With real-time market data integration and intuitive visualization tools, it provides users with powerful insights into their financial portfolios.

---

## Features

### Portfolio Management
- **Combined Investment View**: Monitor assets, liabilities, and portfolio performance in one place.
- **Advanced Analytics**:
  - Investments categorized by sector, macro-sector, industry, and basic classifications.
  - Cumulative dividend tracking since the initial purchase date.
  - Mutual fund financial analysis for portfolio health checks.
- **Stock Trend Visualizations**: Analyze buy volumes to identify trends and improve decision-making.

### Family-Wide Investment Tracking
- Unified view to track and analyze investments for the entire family.
- Centralized dashboard for managing family financial data.

### Real-Time Data Integration
- Live updates with market data fetched from the National Stock Exchange (NSE).
- Asynchronous task management powered by Celery for efficient data fetching and processing.

---

## Technologies

- **Frontend**: React
- **Backend**: Django
- **Task Queue**: Celery with Redis
- **Database**: PostgreSQL
- **Infrastructure**: Docker and Docker Compose
- **Market Data Integration**: NSE API

---

## Installation

### Prerequisites
- Docker and Docker Compose installed.

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/aniket-dg/finsailor.git
   cd finsailor

2. Build and run the application using Docker Compose:
    ```bash
   docker-compose up --build
   ```

