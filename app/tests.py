import json
from datetime import datetime

from django.test import TestCase, Client

from db.models import Table, Booking


class BookingViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.table1 = Table.objects.create(name="Table 1")
        self.table2 = Table.objects.create(name="Table 2")

    def test_get_all_tables(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(len(data["tables"]), 2)

    def test_create_booking(self):
        payload = {
            "client_name": "Ivan",
            "client_phone": "+380999999",
            "table": self.table1.id,
            "date": "01.07.2025T20:00"
        }

        response = self.client.post(
            "/",
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Booking.objects.count(), 1)

    def test_booking_conflict(self):
        date = datetime.strptime("01.07.2025T20:00", "%d.%m.%YT%H:%M")

        Booking.objects.create(
            table=self.table1,
            date=date,
            client_name="Ivan",
            client_phone="+380999"
        )

        payload = {
            "client_name": "Petro",
            "client_phone": "+380888",
            "table": self.table1.id,
            "date": "01.07.2025T21:00"
        }

        response = self.client.post(
            "/",
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 409)

    def test_invalid_date(self):
        payload = {
            "client_name": "Ivan",
            "client_phone": "+380999",
            "table": self.table1.id,
            "date": "wrong-date"
        }

        response = self.client.post(
            "/",
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
