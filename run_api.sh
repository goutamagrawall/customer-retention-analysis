#!/bin/bash
cd backend
PYTHONPATH=/c/Users/ga240/Desktop/crsa/backend uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
