#!/usr/bin/env bash

VERSION=$(<./frontend/version)

docker build -t trainrex/cardboardbound-frontend:$VERSION -t trainrex/cardboardbound-frontend:latest ./frontend
