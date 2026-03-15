from http.server import HTTPServer

from finance_app import FinanceHandler


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), FinanceHandler)
    print("Server running at http://127.0.0.1:8000")
    server.serve_forever()
