
# Automated Weather ETL Pipeline

An automated, end-to-end Data Engineering ETL (Extract, Transform, Load) pipeline that fetches daily weather forecasts for 30+ major cities and stores them in a relational database for downstream analytics.

This project was built to simulate a real-world business use case: **Optimizing outdoor patio seating and inventory management for a global coffee shop chain based on daily weather conditions.**

## Architecture & Data Flow

1. **Extract:** 
   - Dynamically resolves city names to Latitude/Longitude using the **Nominatim OpenStreetMap API**.
   - Pulls the daily weather forecast using the **Open-Meteo REST API**.
2. **Transform:** 
   - Parses deeply nested JSON payloads.
   - Extracts key metrics (Max/Min Temperature, Wind Speed, Wind Gusts, Precipitation).
   - Generates custom business-logic columns (e.g., creating an `is_raining` boolean flag).
3. **Load:** 
   - Loads the cleaned data into a local **SQLite** Data Warehouse.
   - Ensures data idempotency using SQL `INSERT OR IGNORE` and composite `UNIQUE(record_date, city_name)` constraints to prevent duplicate entries.
4. **Automate:** 
   - Orchestrated via **GitHub Actions**. A CRON job triggers the script daily, booting up a virtual runner, executing the Python pipeline, and committing the updated database back to the repository.

## Tech Stack
* **Language:** Python 3.10
* **Libraries:** `requests`, `pandas`, `json`, `sqlite3`, `time`, `os`
* **Database:** SQLite
* **Orchestration / CI/CD:** GitHub Actions
* **External APIs:** Open-Meteo (Weather), Nominatim (Geocoding)

## Key Engineering Features
* **API Caching System:** Implemented a local JSON caching layer (`cityCoords.json`) for geocoding data to dramatically speed up execution time and respect rate-limits of free public APIs.
* **Idempotent Design:** The pipeline can be run multiple times a day without creating duplicate database rows, ensuring data integrity.
* **Modular Codebase:** Code is strictly separated into `extract`, `transform`, and `load` functions for easy testing and scalability.
* **Graceful Error Handling:** `try/except` blocks ensure that if one city's API call fails, the pipeline continues processing the remaining cities without crashing.

## Database Schema (`daily_weather`)

| Column Name | Data Type | Description / Business Logic |
| :--- | :--- | :--- |
| `record_date` | DATE | The date of the weather forecast. |
| `city_name` | TEXT | Name of the city (Target market). |
| `max_temp` | FLOAT | Maximum daily temperature (°C). |
| `min_temp` | FLOAT | Minimum daily temperature (°C). |
| `wind_speed` | FLOAT | Max wind speed (km/h) - Used for patio umbrella safety. |
| `wind_gusts` | FLOAT | Maximum wind gusts (km/h). |
| `wind_direction` | FLOAT | Dominant wind direction. |
| `precipitation` | FLOAT | Total daily precipitation (mm). |
| `is_raining` | BOOLEAN | Custom flag: `True` if precipitation > 0.0, else `False`. |

*(Note: The table uses a composite Primary Key on `record_date` and `city_name`)*

## How to Run Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/Krasper707/weather-etl-pipeline.git
   cd weather-etl-pipeline
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the ETL pipeline:
   ```bash
   python main.py
   ```
4. Check the data! The script will automatically print the contents of the newly updated `coffee_shop.db` file to your terminal using Pandas.

## Automation Details
This pipeline is fully serverless. A GitHub Actions workflow (`.github/workflows/daily_etl.yml`) is scheduled to run at **08:00 UTC every day**. It sets up a Python environment, runs `main.py`, and pushes the updated `.db` file directly to the `main` branch.

## Future Enhancements
- [ ] Migrate the local SQLite database to a cloud **PostgreSQL** instance (Neon/Supabase) to decouple storage from compute.
- [ ] Connect the cloud database to a BI tool (Metabase/Looker Studio) or use Streamlit to build an interactive dashboard.
- [ ] Add unit tests via `pytest` to validate JSON parsing logic.
