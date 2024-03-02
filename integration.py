import unittest
import psycopg2
from pathlib import Path
import asyncio
import sys

BASE_DIR = Path(__file__).resolve().parent

sys.path.append(str(BASE_DIR / 'turistbus_service/app'))
sys.path.append(str(BASE_DIR / 'ticket_service/app'))

from turistbus_service.app.main import turistbus_alive as turistbus_status
from ticket_service.app.main import ticket_alive as ticket_status

class TestIntegration(unittest.TestCase):

    def test_db_connection(self):
        def test_database(self):
            try:
                conn = psycopg2.connect(
                    dbname='turistbusdb',
                    user='panzerknaker',
                    password='1212',
                    host='localhost',
                    port='5432'
                )
                conn.close()
                check = True
            except Exception as e:
                check = False
            self.assertEqual(check, True)

    def test_turistbus_status_connection(self):
        r = asyncio.run(turistbus_status())
        self.assertEqual(r, {'message': 'service alive'})

    def test_ticket_status_connection(self):
        r = asyncio.run(ticket_status())
        self.assertEqual(r, {'message': 'service alive'})


if __name__ == '__main__':
    unittest.main()