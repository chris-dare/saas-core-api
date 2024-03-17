#!/bin/sh -e

docker build . --file backend-image-build.dockerfile --tag chrisdare/serenity-data-bridge-backend:latest
docker image push chrisdare/serenity-data-bridge-backend:latest
