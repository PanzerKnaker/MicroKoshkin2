import asyncio
import unittest
import requests
import psycopg2
from time import sleep
import json
import sys
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

sys.path.append(str(BASE_DIR / 'ticket_service/app'))
sys.path.append(str(BASE_DIR / 'turistbus_service/app'))

from ticket_service.app.main import ticket_alive as doc1
from turistbus_service.app.main import station_alive as doc2

def check_connect():
    try:
        conn = psycopg2.connect(
            dbname='turistbusdb',
            user='panzerknaker',
            password='1212',
            host='localhost',
            port='5432'
        )
        conn.close()
        return True
    except Exception as e:
        return False


class TestIntegration(unittest.TestCase):
    # CMD: python tests/integration.py

    def test_db_connection(self):
        sleep(5)
        self.assertEqual(check_connect(), True)

    def test_ticket_service_connection(self):
        r = asyncio.run(doc1())
        self.assertEqual(r, {'message': 'service is active'})

    def test_turistbus_service_connection(self):
        r = asyncio.run(doc2())
        self.assertEqual(r, {'message': 'service is active'})


if __name__ == '__main__':
    unittest.main()
