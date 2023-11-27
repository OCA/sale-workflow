# Copyright 2024 Akretion - Olivier Nibart
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date, timedelta

import psycopg2

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tools.misc import mute_logger

from .common import TestCommon


class TestSalePrimeship(TestCommon):
    def test_compute_name(self):
        primeship = self.make_primeship("2024-01-01", "2024-12-31")
        self.assertEqual(primeship.name, "2024-01-01 - 2024-12-31 Primeship")

    def test_compute_current(self):
        today = date.today()
        primeship_current = self.make_primeship(
            today - timedelta(days=1), today + timedelta(days=1)
        )
        primeship_past = self.make_primeship(
            today - timedelta(days=10), today - timedelta(days=1)
        )
        primeship_future = self.make_primeship(
            today + timedelta(days=1), today + timedelta(days=10)
        )
        self.assertTrue(primeship_current.current)
        self.assertFalse(primeship_past.current)
        self.assertFalse(primeship_future.current)

    def test_check_end_date(self):
        with self.assertRaises(ValidationError):
            self.make_primeship("2023-12-31", "2023-01-01")

    def test_overlapping_primeships(self):
        self.make_primeship("2023-01-01", "2023-06-30")
        with self.assertRaises(ValidationError):
            self.make_primeship("2023-06-01", "2023-12-31")

    def test_non_overlapping_primeships(self):
        primeship1 = self.make_primeship("2023-01-01", "2023-06-30")
        primeship2 = self.make_primeship("2023-07-01", "2023-12-31")
        self.assertTrue(primeship1.id)
        self.assertTrue(primeship2.id)

    def test_overlaps_method(self):
        primeship = self.make_primeship("2023-01-01", "2023-12-31")
        self.assertTrue(
            primeship.overlaps(
                fields.Date.to_date("2023-06-01"), fields.Date.to_date("2023-07-01")
            )
        )
        self.assertTrue(
            primeship.overlaps(
                fields.Date.to_date("2022-06-01"), fields.Date.to_date("2023-02-01")
            )
        )
        self.assertTrue(
            primeship.overlaps(
                fields.Date.to_date("2023-12-01"), fields.Date.to_date("2024-01-01")
            )
        )
        self.assertFalse(
            primeship.overlaps(
                fields.Date.to_date("2022-01-01"), fields.Date.to_date("2022-12-31")
            )
        )
        self.assertFalse(
            primeship.overlaps(
                fields.Date.to_date("2024-01-01"), fields.Date.to_date("2024-12-31")
            )
        )

    def test_sale_order_line_sale_primeship_o2o_relation_sql_constraint(self):
        order_line = self.make_order_line()
        self.make_primeship("2023-01-01", "2023-12-31", order_line_id=order_line)
        with self.assertRaises(psycopg2.IntegrityError):
            with mute_logger("odoo.sql_db"), self.cr.savepoint():
                self.make_primeship(
                    "2024-01-01", "2024-12-31", order_line_id=order_line
                )
