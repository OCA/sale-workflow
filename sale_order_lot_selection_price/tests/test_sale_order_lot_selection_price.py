# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestSaleOrderLotSelectionPrice(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "type": "consu",
                "is_storable": True,
                "tracking": "lot",
                "standard_price": 5,
                "lst_price": 50,
            }
        )
        cls.lot_a = cls.env["stock.lot"].create(
            {"product_id": cls.product.id, "standard_price": 10, "lst_price": 100}
        )
        cls.lot_b = cls.env["stock.lot"].create(
            {"product_id": cls.product.id, "standard_price": 20, "lst_price": 200}
        )
        cls.pricelist_list_price = cls.env["product.pricelist"].create(
            {
                "company_id": cls.env.company.id,
                "name": "Test pricelist list_price",
                "currency_id": cls.env.company.currency_id.id,
                "item_ids": [
                    Command.create(
                        {
                            "applied_on": "3_global",
                            "compute_price": "formula",
                            "base": "list_price",
                            "price_discount": 10,
                        }
                    )
                ],
            }
        )
        cls.pricelist_standard_price = cls.env["product.pricelist"].create(
            {
                "company_id": cls.env.company.id,
                "name": "Test pricelist standard_price",
                "currency_id": cls.env.company.currency_id.id,
                "item_ids": [
                    Command.create(
                        {
                            "applied_on": "3_global",
                            "compute_price": "formula",
                            "base": "standard_price",
                            "price_discount": 10,
                        }
                    )
                ],
            }
        )

    def test_sale_order_pricelist_list_price(self):
        self.partner.property_product_pricelist = self.pricelist_list_price
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = self.partner
        with order_form.order_line.new() as line_form:
            line_form.product_id = self.product
            line_form.lot_id = self.lot_a
        with order_form.order_line.new() as line_form:
            line_form.product_id = self.product
            line_form.lot_id = self.lot_b
        with order_form.order_line.new() as line_form:
            line_form.product_id = self.product
        order = order_form.save()
        line_lot_a = order.order_line.filtered(lambda x: x.lot_id == self.lot_a)
        self.assertEqual(line_lot_a.price_unit, 90)  # 90=100-10%
        line_lot_b = order.order_line.filtered(lambda x: x.lot_id == self.lot_b)
        self.assertEqual(line_lot_b.price_unit, 180)  # 180=200-10%
        line_without_lot = order.order_line.filtered(lambda x: not x.lot_id)
        self.assertEqual(line_without_lot.price_unit, 45)  # 45=50-10%

    def test_sale_order_pricelist_standard_price(self):
        self.partner.property_product_pricelist = self.pricelist_standard_price
        order_form = Form(self.env["sale.order"])
        order_form.partner_id = self.partner
        with order_form.order_line.new() as line_form:
            line_form.product_id = self.product
            line_form.lot_id = self.lot_a
        with order_form.order_line.new() as line_form:
            line_form.product_id = self.product
            line_form.lot_id = self.lot_b
        with order_form.order_line.new() as line_form:
            line_form.product_id = self.product
        order = order_form.save()
        line_lot_a = order.order_line.filtered(lambda x: x.lot_id == self.lot_a)
        self.assertEqual(line_lot_a.price_unit, 9)  # 9=10-10%
        line_lot_b = order.order_line.filtered(lambda x: x.lot_id == self.lot_b)
        self.assertEqual(line_lot_b.price_unit, 18)  # 18=20-10%
        line_without_lot = order.order_line.filtered(lambda x: not x.lot_id)
        self.assertEqual(line_without_lot.price_unit, 4.5)  # 4.5=5-10%
