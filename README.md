# PostGIS Database Setup

## Overview
This project provides scripts and documentation for setting up a PostGIS-enabled PostgreSQL database.

## Prerequisites
- PostgreSQL installed
- PostGIS extension available
- Administrative database access

## Installation

1. **Install PostgreSQL** (if not already installed)
    ```bash
    # Windows/Mac/Linux installation varies by OS
    ```

2. **Enable PostGIS extension**
    ```sql
    CREATE EXTENSION postgis;
    ```

3. **Verify installation**
    ```sql
    SELECT postgis_version();
    ```

## Usage
[Add your usage instructions here]

## Documentation
- [PostGIS Official Docs](https://postgis.net/documentation/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

## License
[Add your license here]