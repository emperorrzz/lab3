from io import BytesIO
import unittest

from app import Handler


class MemoryConnection:
    """Передаёт HTTP-запрос настоящему обработчику без открытия TCP-порта."""

    def __init__(self, request):
        self.request = request
        self.response = bytearray()

    def makefile(self, mode, buffering=-1):
        return BytesIO(self.request)

    def sendall(self, data):
        self.response.extend(data)


class WebTests(unittest.TestCase):
    def request(self, path="/", data=None):
        body = data.encode() if data is not None else b""
        method = "POST" if data is not None else "GET"
        headers = f"{method} {path} HTTP/1.0\r\nContent-Length: {len(body)}\r\n\r\n"
        connection = MemoryConnection(headers.encode() + body)
        Handler(connection, ("127.0.0.1", 12345), None)
        head, body = bytes(connection.response).split(b"\r\n\r\n", 1)
        return int(head.split()[1]), body.decode("utf-8")

    def test_home_page(self):
        status, body = self.request()
        self.assertEqual(status, 200)
        self.assertIn("Калькулятор ипотеки", body)

    def test_health(self):
        self.assertEqual(self.request("/health"), (200, "ok"))

    def test_calculation_form(self):
        status, body = self.request(data="amount=120000&rate=0&years=1")
        self.assertEqual(status, 200)
        self.assertIn("10,000.00", body)

    def test_bad_input_returns_400(self):
        for data in ("amount=-1&rate=12&years=20", "amount=abc", "amount=1&rate=2&years=1.5"):
            with self.subTest(data=data):
                self.assertEqual(self.request(data=data)[0], 400)

    def test_missing_page(self):
        self.assertEqual(self.request("/missing")[0], 404)

    def test_input_is_escaped(self):
        status, body = self.request(data="amount=%3Cscript%3E&rate=0&years=1")
        self.assertEqual(status, 400)
        self.assertNotIn("<script>", body)
