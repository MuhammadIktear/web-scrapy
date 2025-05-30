# Prothom Alo News Scraper (Django + Scrapy Logic)

This project is a Django application designed to scrape the latest news headlines and their corresponding links from the Prothom Alo website (`https://www.prothomalo.com/collection/latest`). The scraped data is then stored in a local SQLite database. The application is containerized using Docker for easy setup and execution.

## Features

*   Scrapes latest news titles and URLs from Prothom Alo.
*   Stores scraped data into an SQLite database, avoiding duplicates based on URL.
*   Built with Django, using a custom management command for scraping.
*   Utilizes `requests` and `BeautifulSoup4` for web scraping.
*   Containerized with Docker and Docker Compose for portability and ease of use.

## Technologies Used

*   **Backend:** Python, Django
*   **Web Scraping:** `requests`, `BeautifulSoup4`, `lxml`
*   **Database:** SQLite
*   **WSGI Server:** Gunicorn (within Docker)
*   **Containerization:** Docker, Docker Compose

## Prerequisites

*   Docker installed on your system.
*   Docker Compose installed on your system.

## Getting Started

1.  **Clone the Repository (if applicable):**
    If you have this project in a Git repository, clone it first.
    ```bash
    # git clone <your-repository-url>
    # cd <your-repository-directory>
    ```
    If you are just setting up from the provided files, ensure all necessary files (`Dockerfile`, `docker-compose.yml`, `entrypoint.sh`, `requirements.txt`, your Django project structure) are in the same root directory.

2.  **Create a `.env` file:**
    In the project root directory (where `docker-compose.yml` is located), create a file named `.env` with the following content. **Replace the `SECRET_KEY` with a strong, unique key.**
    ```ini
    # .env
    SECRET_KEY=your_very_strong_and_unique_secret_key_here_CHANGE_ME
    DEBUG=True
    ALLOWED_HOSTS=127.0.0.1,localhost
    ```
    *   `DEBUG=True` is suitable for development. For production, set it to `False`.
    *   `ALLOWED_HOSTS` should include any hosts you'll access the app from.

3.  **Ensure `requirements.txt` is present and up-to-date:**
    This file should list all Python dependencies. If not present, create it from your virtual environment:
    ```bash
    # pip freeze > requirements.txt
    ```
    It should include at least: `Django`, `requests`, `beautifulsoup4`, `lxml`, `gunicorn`, `python-dotenv`.

4.  **Build and Run with Docker Compose:**
    From the project root directory, run the following commands:
    ```bash
    docker-compose build
    docker-compose up -d
    ```
    This will build the Docker image (if not already built) and start the Django application container in detached mode. The application will be accessible at `http://localhost:8000`.

## Running the Scraper

The scraping logic is implemented as a Django management command. To run the scraper after the application container is up:

1.  **Execute the `scrape_news` command:**
    ```bash
    docker-compose exec web python manage.py scrape_news
    ```
    This command will fetch the latest news from Prothom Alo and store new articles in the `db_sqlite/db.sqlite3` file (which is persisted via a Docker volume).

## Project Structure Overview

The key files for Dockerization are:

*   **`Dockerfile`**: Defines how to build the Docker image for the Django application.
*   **`docker-compose.yml`**: Defines and runs the multi-container Docker application (in this case, a single `web` service).
    ```yaml
    version: "3.9"

    services:
      web:
        build: .
        ports:
          - "8000:8000"
        volumes:
          - .:/app # Mounts current directory to /app in container (good for development)
          - sqlite_db_volume:/app/db_sqlite # Persists SQLite database
          - staticfiles_volume:/app/staticfiles # Persists static files
          - mediafiles_volume:/app/mediafiles   # Persists media files
        env_file:
          - .env
        # The command to run Gunicorn is now in the Dockerfile's CMD,
        # but entrypoint.sh will execute it.
        # If you need to override Dockerfile's CMD:
        # command: gunicorn scrapy.wsgi:application --bind 0.0.0.0:8000
        entrypoint: ["/app/entrypoint.sh"] # Ensures migrations etc., run first
        restart: unless-stopped

    volumes:
      sqlite_db_volume:
      staticfiles_volume:
      mediafiles_volume:
    ```
*   **`entrypoint.sh`**: A script that runs when the container starts. It handles:
    *   Creating necessary directories (like `db_sqlite`).
    *   Applying database migrations (`python manage.py migrate`).
    *   Collecting static files (`python manage.py collectstatic`).
    *   Finally, executing the main command (Gunicorn server).
*   **`requirements.txt`**: Lists Python package dependencies.
*   **`.env`**: Stores environment variables (like `SECRET_KEY`). **Do not commit this file to Git.**
*   **`.dockerignore`**: Specifies files and directories to exclude when building the Docker image.
*   **`.gitignore`**: Specifies intentionally untracked files that Git should ignore.

## Accessing the Application

*   **Web Application:** `http://localhost:8000`
*   **Django Admin:** `http://localhost:8000/admin/` (You'll need to create a superuser first if you haven't: `docker-compose exec web python manage.py createsuperuser`)

## Database

This project uses SQLite. The database file (`db.sqlite3`) is stored inside the `db_sqlite` directory within the container, which is mapped to a Docker named volume (`sqlite_db_volume`) for persistence. This means your data will remain even if you stop and remove the container (unless you also remove the volume).

## Important Notes for Users

*   **Website Structure Changes:** Web scraping is highly dependent on the target website's HTML structure. If Prothom Alo changes its website layout, the scraper (`scrape_news.py`) might need to be updated with new selectors.
*   **Ethical Scraping:** Always be respectful of the target website's resources. Do not scrape too frequently to avoid overloading their servers. Check their `robots.txt` and Terms of Service if available.
*   **Development vs. Production:**
    *   The current `docker-compose.yml` mounts the local project directory (`.:/app`). This is great for development as code changes are reflected immediately (with Gunicorn's reload or Django dev server). For production, you would typically build an image with the code copied in, and not use this live-mount.
    *   `DEBUG=True` should be `False` in a production environment.
    *   For a production setup, consider using a more robust database like PostgreSQL instead of SQLite.

## Troubleshooting

*   **"DisallowedHost" error:** Ensure `ALLOWED_HOSTS` in your `.env` file includes `localhost` and `127.0.0.1`.
*   **Scraper not finding articles:** The HTML structure of Prothom Alo might have changed. You'll need to inspect their website and update the selectors in `my_app/management/commands/scrape_news.py`.
*   **Permissions issues with volumes (Linux):** If you encounter permission errors with mounted volumes, you might need to adjust file ownership or permissions on your host machine, or configure the user inside the Docker container.

---
This README provides a good starting point for anyone wanting to run your project. Remember to replace placeholders like `<your-repository-url>` if you host this on GitHub.