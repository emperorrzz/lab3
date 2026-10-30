"""Консольный калькулятор ипотеки."""
import argparse

from calculator import calculate_mortgage

TITLE = "Калькулятор ипотеки"


def main(argv=None):
    parser = argparse.ArgumentParser(description=TITLE)
    parser.add_argument("--amount", type=float, help="Сумма кредита в рублях")
    parser.add_argument("--rate", type=float, help="Годовая ставка в процентах")
    parser.add_argument("--years", type=int, help="Срок в годах")
    args = parser.parse_args(argv)
    try:
        amount = args.amount if args.amount is not None else float(input("Сумма кредита: "))
        rate = args.rate if args.rate is not None else float(input("Годовая ставка (%): "))
        years = args.years if args.years is not None else int(input("Срок (лет): "))
        result = calculate_mortgage(amount, rate, years)
    except (ValueError, EOFError) as error:
        parser.exit(2, f"Ошибка ввода: {error}\n")
    print(TITLE)
    print(f"Ежемесячный платёж: {result.monthly_payment:.2f} руб.")
    print(f"Всего выплат: {result.total_payment:.2f} руб.")
    print(f"Переплата: {result.overpayment:.2f} руб.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
