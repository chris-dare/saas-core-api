#!/bin/sh -e

docker build . --file backend-image-build.dockerfile --tag chrisdare/senta-core-api-backend:latest
docker image push chrisdare/senta-core-api-backend:latest