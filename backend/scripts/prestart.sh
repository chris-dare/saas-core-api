#! /usr/bin/env bash

# Let the DB start
python /app/data_bridge/backend_pre_start.py

# Run migrations
alembic upgrade head

# Create initial data in DB
python /app/data_bridge/initial_data.py
