#!/usr/bin/env bash

VERSION=$(<./frontend/version)

docker push trainrex/cardboardbound-frontend:$VERSION
docker push trainrex/cardboardbound-frontend:latest
