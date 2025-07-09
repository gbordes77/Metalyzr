#!/bin/bash
cd "/Users/guillaumebordes/Documents/Metalyzr /backend"
pkill -f uvicorn
sleep 2
python3 -m uvicorn main_simple:app --host 0.0.0.0 --port 8000 