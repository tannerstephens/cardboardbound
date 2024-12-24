#!/usr/bin/env bash

VERSION=$(<./backend/version)

docker push trainrex/cardboardbound-backend:$VERSION
docker push trainrex/cardboardbound-backend:latest
