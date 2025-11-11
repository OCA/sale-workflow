# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date, timedelta

from odoo import Command
from odoo.tests import TransactionCase


class TestSalePricelistDeliveryDate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product = cls.env["product.product"].create({"name": "Test Product"})
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Custom Pricelist (TEST)",
                "sequence": 4,
                "currency_id": cls.env.company.currency_id.id,
                "item_ids": [
                    Command.create(
                        {
                            "base": "list_price",
                            "applied_on": "1_product",
                            "min_quantity": 1,
                            "product_tmpl_id": cls.product.product_tmpl_id.id,
                            "compute_price": "fixed",
                            "fixed_price": 100.0,
                            "date_start": date.today(),
                            "date_end": date.today() + timedelta(days=1),
                        }
                    ),
                    Command.create(
                        {
                            "base": "list_price",
                            "applied_on": "1_product",
                            "min_quantity": 1,
                            "product_tmpl_id": cls.product.product_tmpl_id.id,
                            "compute_price": "fixed",
                            "fixed_price": 150.0,
                            "date_start": date.today() + timedelta(days=2),
                            "date_end": date.today() + timedelta(days=3),
                        }
                    ),
                ],
            }
        )
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "pricelist_id": cls.pricelist.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                        }
                    )
                ],
            }
        )

    def test_sale_order_pricelist_delivery_date(self):
        self.assertEqual(self.sale_order.order_line.price_unit, 100.0)
        self.sale_order.company_id.use_delivery_date_price = True
        self.sale_order.commitment_date = date.today() + timedelta(days=2)
        self.assertEqual(self.sale_order.order_line.price_unit, 150.0)
        self.sale_order.commitment_date = False
        self.assertEqual(self.sale_order.order_line.price_unit, 100.0)
        self.sale_order.order_line.customer_lead = 2
        self.assertEqual(self.sale_order.order_line.price_unit, 150.0)
        self.sale_order.commitment_date = date.today() + timedelta(days=1)
        self.assertEqual(self.sale_order.order_line.price_unit, 100.0)
