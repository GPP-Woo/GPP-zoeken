from datetime import date, datetime

from django.test import SimpleTestCase

from woo_search.utils.date import TIMEZONE_AMS, date_to_datetime


class DateToDatetimeTest(SimpleTestCase):
    def test_timezone_amsterdam(self):
        converted_datetime = date_to_datetime(date(2025, 1, 1))

        self.assertEqual(
            converted_datetime,
            datetime(2025, 1, 1, 0, 0, 0, tzinfo=TIMEZONE_AMS),
        )
