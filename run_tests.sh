#!/bin/bash
set -e

echo "=== API EXTRACTION ==="
cd lm-api-extraction
python3 -m unittest discover -v
python3 test_bulk.py

echo "=== CACHE COLLECTOR ==="
cd ../lm-cache-collector
python3 -m unittest test_messages -v
node test_message_stream.cjs

echo "=== TELEGRAM BOT ==="
cd ../lm-telegram-bot
python3 -m unittest test_bot -v

echo "=== ALL TESTS PASSED ==="
