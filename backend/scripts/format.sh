#!/bin/sh -e
set -x

# autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place app --exclude=__init__.py --exclude=migrations/
autoflake --recursive --remove-unused-variables --in-place app --exclude=__init__.py --exclude=migrations/
black app
isort --recursive --apply app
