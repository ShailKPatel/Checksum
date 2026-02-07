@echo off
echo Starting Checksum Verifier...
echo Opening Sender and Receiver pages...
start http://127.0.0.1:8000/sender
start http://127.0.0.1:8000/receiver
echo Server running at http://127.0.0.1:8000
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
pause
