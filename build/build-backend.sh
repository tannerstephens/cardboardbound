#!/usr/bin/env bash

VERSION=$(<./backend/version)

docker build -t trainrex/cardboardbound-backend:$VERSION -t trainrex/cardboardbound-backend:latest ./backend
