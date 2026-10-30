import unittest

from calculator import calculate_mortgage


class MortgageTests(unittest.TestCase):
    def test_known_annuity_payment(self):
        result = calculate_mortgage(3_000_000, 12, 20)
        self.assertEqual(result.monthly_payment, 33032.58)
        self.assertEqual(result.total_payment, 7927820.16)
        self.assertEqual(result.overpayment, 4927820.16)

    def test_zero_rate(self):
        result = calculate_mortgage(120_000, 0, 1)
        self.assertEqual(result.monthly_payment, 10000)
        self.assertEqual(result.total_payment, 120000)
        self.assertEqual(result.overpayment, 0)

    def test_tiny_rate_does_not_cause_division_by_zero(self):
        result = calculate_mortgage(120_000, 1e-20, 1)
        self.assertEqual(result.monthly_payment, 10000)

    def test_longer_term_reduces_payment_but_increases_overpayment(self):
        short = calculate_mortgage(1_000_000, 10, 10)
        long = calculate_mortgage(1_000_000, 10, 20)
        self.assertLess(long.monthly_payment, short.monthly_payment)
        self.assertGreater(long.overpayment, short.overpayment)

    def test_higher_rate_increases_payment(self):
        self.assertGreater(calculate_mortgage(1_000_000, 15, 10).monthly_payment,
                           calculate_mortgage(1_000_000, 5, 10).monthly_payment)

    def test_invalid_amounts(self):
        for amount in (0, -1, 1_000_000_001, float("nan"), float("inf")):
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                calculate_mortgage(amount, 12, 20)

    def test_invalid_rates(self):
        for rate in (-1, 101, float("nan"), float("inf")):
            with self.subTest(rate=rate), self.assertRaises(ValueError):
                calculate_mortgage(100000, rate, 20)

    def test_invalid_terms(self):
        for years in (0, -1, 51, 1.5, True):
            with self.subTest(years=years), self.assertRaises(ValueError):
                calculate_mortgage(100000, 12, years)


if __name__ == "__main__":
    unittest.main()
