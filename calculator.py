"""Аннуитетный платёж; суммы результата округляются до копеек."""

from dataclasses import dataclass
from math import expm1, isfinite, log1p


@dataclass(frozen=True)
class Mortgage:
    monthly_payment: float
    total_payment: float
    overpayment: float


def calculate_mortgage(amount: float, annual_rate: float, years: int) -> Mortgage:
    if not isfinite(amount) or not 0 < amount <= 1_000_000_000:
        raise ValueError("Сумма должна быть больше 0 и не больше 1 млрд рублей.")
    if not isfinite(annual_rate) or not 0 <= annual_rate <= 100:
        raise ValueError("Ставка должна быть от 0 до 100 процентов.")
    if isinstance(years, bool) or not isinstance(years, int) or not 1 <= years <= 50:
        raise ValueError("Срок должен быть целым числом от 1 до 50 лет.")
    months = years * 12
    rate = annual_rate / 1200
    payment = amount / months if rate == 0 else amount * rate / -expm1(-months * log1p(rate))
    total = payment * months
    return Mortgage(round(payment, 2), round(total, 2), round(total - amount, 2))
