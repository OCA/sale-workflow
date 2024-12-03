# Copyright 2024 Akretion - Clément Mombereau
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import Form, TransactionCase


class TestSaleOrderQtyChangeNoZero(TransactionCase):
    def setUp(self):
        super().setUp()
        self.product_1 = self.env["product.product"].create(
            {"name": "Test Product 1", "list_price": 0, "taxes_id": False}
        )
        self.product_2 = self.env["product.product"].create(
            {"name": "Test Product 2", "list_price": 30.00, "taxes_id": False}
        )
        pricelist = self.env["product.pricelist"].create({"name": "Test pricelist"})
        sale_form = Form(self.env["sale.order"])
        sale_form.partner_id = self.env.ref("base.res_partner_12")
        sale_form.pricelist_id = pricelist
        with sale_form.order_line.new() as self.line_form:
            self.line_form.product_id = self.product_1
            self.line_form.product_uom_qty = 1

    def test_product_with_lst_price_zero(self):
        self.line_form.price_unit = 10
        self.assertEqual(self.line_form.price_unit, 10)
        self.assertEqual(self.line_form.price_subtotal, 10)
        self.line_form.product_uom_qty = 2
        self.assertEqual(self.line_form.price_unit, 10)
        self.assertEqual(self.line_form.price_subtotal, 20)

    def test_product_with_lst_price_not_zero(self):
        self.line_form.product_id = self.product_2
        self.line_form.product_uom_qty = 2
        self.assertEqual(self.line_form.price_unit, 30)
        self.assertEqual(self.line_form.price_subtotal, 60)
        self.line_form.price_unit = 10
        self.assertEqual(self.line_form.price_unit, 10)
        self.assertEqual(self.line_form.price_subtotal, 20)
        self.line_form.product_uom_qty = 1
        self.assertEqual(self.line_form.price_unit, 30)
        self.assertEqual(self.line_form.price_subtotal, 30)
