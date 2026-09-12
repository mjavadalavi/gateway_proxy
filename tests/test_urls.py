from unittest import TestCase

from utils.urls import append_query_parameters


class AppendQueryParametersTests(TestCase):
    def test_appends_to_an_existing_signed_callback_query(self) -> None:
        result = append_query_parameters(
            "https://homay.space/payments/callback?state=signed-token",
            Authority="A0001",
            Status="OK",
        )

        self.assertEqual(
            result,
            "https://homay.space/payments/callback?state=signed-token&Authority=A0001&Status=OK",
        )

    def test_preserves_a_fragment(self) -> None:
        result = append_query_parameters(
            "https://example.com/callback#result",
            Status="NOK",
        )

        self.assertEqual(
            result,
            "https://example.com/callback?Status=NOK#result",
        )
