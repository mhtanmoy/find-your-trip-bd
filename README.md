# Find You Trip BD

**Find You Trip BD** is a Django-based REST API that helps you discover the top 10 travel destinations in Bangladesh based on **weather conditions** and **air quality**. The API provides endpoints to fetch temperature and air quality data, as well as personalized travel recommendations based on a given location and date.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Dependencies](#dependencies)
- [Setup Using Docker](#setup-using-docker)
  - [Clone the Repository](#clone-the-repository)
  - [Create a `.env` File](#create-a-env-file)
  - [Build and Start the Docker Containers](#build-and-start-the-docker-containers)
  - [Access the API](#access-the-api)
- [API Documentation](#api-documentation)
- [Notes](#notes)
- [Local Development (Optional)](#local-development-optional)


## Prerequisites

Before setting up the project, make sure you have the following installed:

- **Docker** (version 20.10.21 or later)
- **Docker Compose** (compatible with your Docker version)
- **Python 3.12** (only if you prefer to run locally outside Docker)

## Dependencies

The following dependencies are required for the project:

- **Django** 5.2
- **Django REST Framework** 3.16.0
- **Celery** 5.5.1
- **Django Celery Beat** 2.8.0
- **Psycopg2-binary** 2.9.10 (PostgreSQL adapter)
- **Redis** 5.2.1
- **Numpy** 2.2.4
- **Pandas** 2.2.3
- **Requests** 2.32.3
- **OpenMeteo SDK** 1.20.0
- **OpenMeteo Requests** 1.4.0

## Setup Using Docker

To set up the project using Docker, follow these steps:

### Clone the Repository

Start by cloning the repository to your local machine:

```
git clone https://github.com/mhtanmoy/find-your-trip-bd.git
cd find-you-trip-bd
```

## Create a `.env` File

The project uses environment variables for various configurations (such as database connection, secret key, and caching). 

1. Create a `.env` file in the root of the project directory.
2. Copy the contents from the `.env.example` file:

    ```
    cp .env.example .env
    ```

3. Edit the `.env` file with the necessary values. A typical `.env` file should include:

    ```
    SECRET_KEY=your-secret-key
    DEBUG=True
    ALLOWED_HOSTS="*"
    DB_NAME=tripdb
    DB_USER=postgres
    DB_PASSWORD=1234
    DB_HOST=db
    DB_PORT=5432
    DISTRICT_DATA_URL=https://raw.githubusercontent.com/strativ-dev/technical-screening-test/main/bd-districts.json
    WEATHER_API_URL = https://api.open-meteo.com/v1/forecas
    AIR_QUALITY_API_URL = https://air-quality-api.open-meteo.com/v1/air-quality
    POSTGRES_DB=tripdb
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=1234
    REDIS_HOST=redis
    REDIS_PORT=6379
    ```

   Replace `your-secret-key` with a secure secret key for your Django application.


## Build and Start the Docker Containers

Now, build and start the Docker containers using Docker Compose:

```
docker-compose up --build
```
This command will pull the necessary Docker images (if not already available), build the containers, and start the services.

## Access the API
Once the application is running, you can access the API on the following URL:

### Base URL: http://127.0.0.1:8000

API Documentation
Once the server is running, you can access the interactive API documentation using Swagger UI:

## Swagger UI: http://127.0.0.1:8000/docs

This interface allows you to explore the available API endpoints and try out requests directly from your browser.

## Notes
Make sure all services (Django, PostgreSQL, Redis, Initials Tasks) are up and running before making API calls.

If you're running the application locally without Docker, make sure to install the required dependencies by running:

```
pip install -r requirements.txt
```
You'll also need to configure PostgreSQL and Redis locally.