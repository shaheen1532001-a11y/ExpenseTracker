import os
import sys
import sqlite3
import tempfile
import unittest

sys.path.insert(0, os.path.abspath("src"))

import app as app_module


class ExpenseTrackerTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        app_module.DB = os.path.join(self.temp_dir.name, "test.db")
        app_module.init_db()
        self.client = app_module.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_add_income(self):
        response = self.client.post("/add", data={
            "description": "Salary",
            "amount": "5000",
            "type": "Income",
            "category": "Salary"
        })
        self.assertEqual(response.status_code, 302)

        conn = sqlite3.connect(app_module.DB)
        count = conn.execute(
            "SELECT COUNT(*) FROM transactions"
        ).fetchone()[0]
        conn.close()

        self.assertEqual(count, 1)

    def test_delete_transaction(self):
        self.client.post("/add", data={
            "description": "Lunch",
            "amount": "200",
            "type": "Expense",
            "category": "Food"
        })

        conn = sqlite3.connect(app_module.DB)
        transaction_id = conn.execute(
            "SELECT id FROM transactions"
        ).fetchone()[0]
        conn.close()

        response = self.client.post(f"/delete/{transaction_id}")
        self.assertEqual(response.status_code, 302)

        conn = sqlite3.connect(app_module.DB)
        count = conn.execute(
            "SELECT COUNT(*) FROM transactions"
        ).fetchone()[0]
        conn.close()

        self.assertEqual(count, 0)


if __name__ == "__main__":
    unittest.main()