# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from freezegun import freeze_time

from odoo.tests import Form, TransactionCase


@freeze_time("2018-01-11")
class TestSaleOrderSafeCommitmentDate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        sale_form = Form(cls.env["sale.order"])
        sale_form.partner_id = cls.env["res.partner"].create({"name": "Mr. Odoo"})
        with sale_form.order_line.new() as line:
            line.product_id = cls.env["product.product"].create({"name": "Test thingy"})
        cls.sale_order = sale_form.save()

    def test_unsafe_commitment_date(self):
        """Time is freezed at 2018-01-11. As there aren't lead times, expected date
        will be that date. Any date previous to that one is unsafe"""
        self.assertFalse(self.sale_order.is_commitment_date_unsafe)
        # Always in the past. Impossible to fullfil
        self.sale_order.commitment_date = "2018-01-10"
        self.assertTrue(self.sale_order.is_commitment_date_unsafe)
        self.sale_order.action_confirm()
        self.assertFalse(self.sale_order.is_commitment_date_unsafe)
        self.assertEqual(self.sale_order.commitment_date, self.sale_order.expected_date)

    def test_safe_commitment_date(self):
        """Time is freezed at 2018-01-11. There aren't lead times and the commitment
        date is set after the expected date"""
        self.assertFalse(self.sale_order.is_commitment_date_unsafe)
        self.sale_order.commitment_date = "2018-01-20"
        self.assertFalse(self.sale_order.is_commitment_date_unsafe)
        self.sale_order.action_confirm()
        self.assertFalse(self.sale_order.is_commitment_date_unsafe)
        self.assertEqual(
            self.sale_order.commitment_date.date().isoformat(), "2018-01-20"
        )
