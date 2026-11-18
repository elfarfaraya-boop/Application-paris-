#!/bin/bash

cd ../
gunicorn -k gthread --threads 4 --timeout 120 -b 0.0.0.0:${PORT:-5000} app:app
