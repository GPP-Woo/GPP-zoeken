"""
Unit test the serializer used for the search endpoint.
"""

from django.test import SimpleTestCase
from django.utils.translation import gettext as _

from ..api.serializers import SearchSerializer
from ..constants import ResultTypeChoices


class SerializerValidationTests(SimpleTestCase):

    def test_validate_creatiedatum(self):
        with self.subTest("no dates given", result_type="document"):
            serializer1 = SearchSerializer(
                data={
                    "result_types": ["document"],
                    "creatiedatum_vanaf": None,
                    "creatiedatum_tot_en_met": None,
                }
            )

            self.assertTrue(serializer1.is_valid())

        with self.subTest("from date given", result_type="document"):
            serializer2 = SearchSerializer(
                data={
                    "result_types": ["document"],
                    "creatiedatum_vanaf": "2024-01-01",
                    "creatiedatum_tot_en_met": None,
                }
            )

            self.assertTrue(serializer2.is_valid())

        with self.subTest("to date given", result_type="document"):
            serializer3 = SearchSerializer(
                data={
                    "result_types": ["document"],
                    "creatiedatum_vanaf": None,
                    "creatiedatum_tot_en_met": "2024-01-01",
                }
            )

            self.assertTrue(serializer3.is_valid())

        for result_type in ResultTypeChoices:
            if result_type == ResultTypeChoices.document:
                continue

            with self.subTest("no dates given", result_type=result_type):
                serializer1 = SearchSerializer(
                    data={
                        "result_types": [result_type],
                        "creatiedatum_vanaf": None,
                        "creatiedatum_tot_en_met": None,
                    }
                )

                self.assertTrue(serializer1.is_valid())

            with self.subTest("from date given", result_type=result_type):
                serializer2 = SearchSerializer(
                    data={
                        "result_types": [result_type],
                        "creatiedatum_vanaf": "2024-01-01",
                        "creatiedatum_tot_en_met": None,
                    }
                )

                self.assertFalse(serializer2.is_valid())
                self.assertIn("non_field_errors", serializer2.errors)
                self.assertEqual(
                    serializer2.errors["non_field_errors"][0],
                    _(
                        "You can only filter on creatiedatum when the result type is "
                        "restricted to 'document', as publications don't have this field."
                    ),
                )

            with self.subTest("to date given", result_type=result_type):
                serializer3 = SearchSerializer(
                    data={
                        "result_types": [result_type],
                        "creatiedatum_vanaf": None,
                        "creatiedatum_tot_en_met": "2024-01-01",
                    }
                )

                self.assertFalse(serializer3.is_valid())
                self.assertIn("non_field_errors", serializer3.errors)
                self.assertEqual(
                    serializer3.errors["non_field_errors"][0],
                    _(
                        "You can only filter on creatiedatum when the result type is "
                        "restricted to 'document', as publications don't have this field."
                    ),
                )
