import requests
import unittest
import json

ticket_service_url = 'http://localhost:8001'
check_turistbus_existence_url = f'{ticket_service_url}/find_bus'

turistbus_service_url = 'http://localhost:8000'
add_turistbus_url = f'{turistbus_service_url}/add_TuristBus'
delete_turistbus_url = f'{turistbus_service_url}/delete_TuristBus'

bustest ={
    'id': 0,
    'modelbus': 'test',
    'destination': 'testdest',
    'datego': '2024-02-25T21:46:30.477000',
    'seats': 666}


class TestComponent(unittest.TestCase):

    def test_1_add_turistbusn(self):
        res = requests.post(f"{add_turistbus_url}", json=bustest)
        self.assertTrue(res.status_code, 200)

    def test_2_check_turistbus_existence(self):
        res = requests.get(f"{check_turistbus_existence_url}?destinationbus=testdest").json()
        self.assertEqual(res, bustest)

    def test_3_delete_turistbus(self):
       res = requests.delete(f"{delete_turistbus_url}?turistbus_id=0")
       self.assertEqual(res.text, '"Success"')

if __name__ == '__main__':
    unittest.main()