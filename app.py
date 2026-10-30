"""Учебное веб-приложение без сторонних зависимостей. Python 3.9+."""

import argparse
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from calculator import calculate_mortgage


TITLE = "Калькулятор ипотеки"


def render_page(values=None, message=""):
    values = values or {"amount": "3000000", "rate": "12", "years": "20"}
    fields = []
    for name, label, step in [("amount", "Сумма кредита, ₽", "0.01"),
                              ("rate", "Годовая ставка, %", "0.01"),
                              ("years", "Срок, лет", "1")]:
        value = escape(values.get(name, ""), quote=True)
        fields.append(f'<label>{label}<input type="number" step="{step}" '
                      f'name="{name}" value="{value}" required></label>')
    version_file = Path(__file__).with_name("VERSION")
    version = escape(version_file.read_text().strip()) if version_file.exists() else "local"
    return f'''<!doctype html><html lang="ru"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title><style>
body{{font:18px system-ui;background:#eef2f6;color:#17283b;margin:0;padding:32px}}
main{{max-width:600px;margin:auto;background:white;border-radius:16px;padding:32px}}
label{{display:block;margin:20px 0}}input,button{{box-sizing:border-box;width:100%;padding:12px;font:inherit}}
input{{margin-top:8px;border:1px solid #aab7c4;border-radius:6px}}
button{{background:#2158b0;color:white;border:0;border-radius:6px;cursor:pointer}}
small{{color:#526173}}.result{{margin:24px 0;line-height:1.7}}
</style><main><h1>{TITLE}</h1><p>Расчёт аннуитетного платежа</p>
<form method="post">{"".join(fields)}<button>Рассчитать</button></form>
<div class="result" role="status">{message}</div>
<p><small>Учебный расчёт без комиссий и страховок. Итог вычисляется до округления
ежемесячного платежа; банковский график может отличаться.</small></p>
<small>Версия: {version}</small></main></html>'''


class Handler(BaseHTTPRequestHandler):
    def respond(self, status, content, content_type="text/html; charset=utf-8"):
        body = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self.respond(200, "ok", "text/plain; charset=utf-8")
        elif self.path == "/":
            self.respond(200, render_page())
        else:
            self.respond(404, "Страница не найдена")

    def do_POST(self):
        if self.path != "/":
            self.respond(404, "Страница не найдена")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 4096:
                raise ValueError("Некорректный размер запроса.")
            data = parse_qs(self.rfile.read(length).decode("utf-8"), keep_blank_values=True)
            values = {key: data.get(key, [""])[0] for key in ("amount", "rate", "years")}
            result = calculate_mortgage(float(values["amount"]), float(values["rate"]), int(values["years"]))
        except (ValueError, UnicodeError) as error:
            self.respond(400, render_page(message="Ошибка ввода: " + escape(str(error))))
            return
        message = (f"Платёж в месяц: <b>{result.monthly_payment:,.2f} ₽</b><br>"
                   f"Всего выплат: {result.total_payment:,.2f} ₽<br>"
                   f"Переплата: {result.overpayment:,.2f} ₽")
        self.respond(200, render_page(values, message))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
