from http.server import HTTPServer

from finance_app import FinanceHandler

import os


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    server = HTTPServer(("0.0.0.0", port), FinanceHandler)
    print(f"Server running on 0.0.0.0:{port}")
    server.serve_forever()
