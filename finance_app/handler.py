from __future__ import annotations

import json
from decimal import Decimal
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

from .constants import DEFAULT_BUDGETS
from .frontend import FinancePageRenderer
from .parsers import FinanceApiParser, FinanceFormParser
from .service import FinanceService


class FinanceHandler(BaseHTTPRequestHandler):
    service = FinanceService(DEFAULT_BUDGETS)
    renderer = FinancePageRenderer()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self._serve_page()
            return
        self._send_json({"error": "Not Found"}, status=404)

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/calculate":
            self._handle_api_calculate()
            return
        if path == "/calculate":
            self._handle_form_calculate()
            return
        self._send_json({"error": "Not Found"}, status=404)

    def _serve_page(self):
        summary = self.service.build_summary(Decimal("0"), {})
        html = self.renderer.render(summary).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html)))
        self.end_headers()
        self.wfile.write(html)

    def _handle_form_calculate(self):
        raw_data = self._read_body()
        salary, budgets = FinanceFormParser.parse_form(raw_data)
        summary = self.service.build_summary(salary, budgets)
        html = self.renderer.render(summary).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html)))
        self.end_headers()
        self.wfile.write(html)

    def _handle_api_calculate(self):
        raw_data = self._read_body()
        salary, budgets = FinanceApiParser.parse_json(raw_data)
        summary = self.service.build_summary(salary, budgets)
        self._send_json(
            {
                "salary": str(summary.salary),
                "total": str(summary.total),
                "remaining": str(summary.remaining),
                "budgets": [
                    {"label": label, "amount": str(amount)}
                    for label, amount in summary.budgets.items()
                ],
            }
        )

    def _read_body(self) -> str:
        content_length = int(self.headers.get("Content-Length", "0"))
        return self.rfile.read(content_length).decode("utf-8")

    def _send_json(self, payload: dict, status: int = 200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)