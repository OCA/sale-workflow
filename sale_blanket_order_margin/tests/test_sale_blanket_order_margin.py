from datetime import date, timedelta

from odoo import fields
from odoo.tests import common


class TestSaleBlanketOrdersMargin(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.blanket_order_obj = self.env["sale.blanket.order"]
        self.blanket_order_line_obj = self.env["sale.blanket.order.line"]
        self.blanket_order_wiz_obj = self.env["sale.blanket.order.wizard"]
        self.so_obj = self.env["sale.order"]

        self.payment_term = self.env.ref("account.account_payment_term_immediate")
        self.sale_pricelist = self.env["product.pricelist"].create(
            {"name": "Test Pricelist", "currency_id": self.env.ref("base.USD").id}
        )

        # UoM
        self.categ_unit = self.env.ref("uom.product_uom_categ_unit")
        self.uom_dozen = self.env["uom.uom"].create(
            {
                "name": "Test-DozenA",
                "category_id": self.categ_unit.id,
                "factor_inv": 12,
                "uom_type": "bigger",
                "rounding": 0.001,
            }
        )

        self.partner = self.env["res.partner"].create(
            {
                "name": "TEST CUSTOMER",
                "property_product_pricelist": self.sale_pricelist.id,
            }
        )

        self.product = self.env["product.product"].create(
            {
                "name": "Demo",
                "categ_id": self.env.ref("product.product_category_1").id,
                "standard_price": 700.0,
                "type": "consu",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "default_code": "PROD_DEL01",
            }
        )
        self.product2 = self.env["product.product"].create(
            {
                "name": "Demo 2",
                "categ_id": self.env.ref("product.product_category_1").id,
                "standard_price": 700.0,
                "type": "consu",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "default_code": "PROD_DEL02",
            }
        )

        self.yesterday = date.today() - timedelta(days=1)
        self.tomorrow = date.today() + timedelta(days=1)

    def test_sale_blanket_order_margin(self):
        """Create a blanket order with two lines and test margins"""
        blanket_order = self.blanket_order_obj.create(
            {
                "partner_id": self.partner.id,
                "validity_date": fields.Date.to_string(self.tomorrow),
                "payment_term_id": self.payment_term.id,
                "pricelist_id": self.sale_pricelist.id,
            }
        )
        blanket_order.sudo().onchange_partner_id()
        blanket_order.write(
            {
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Blanket line Demo 1",
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "original_uom_qty": 10.0,
                            "price_unit": 1000.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Blanket line Demo 2",
                            "product_id": self.product2.id,
                            "product_uom": self.product.uom_id.id,
                            "original_uom_qty": 10.0,
                            "price_unit": 1000.0,
                        },
                    ),
                ],
            }
        )
        blanket_order.sudo().action_confirm()
        self.assertEqual(blanket_order.line_ids[0].margin, 3000.00)
        self.assertEqual(blanket_order.margin, 6000.00)
        self.assertEqual(blanket_order.margin_percent, 0.3)
        blanket_order.line_ids[0].purchase_price = 800
        self.assertEqual(blanket_order.margin, 5000.00)

    def test_sale_blanket_margin_negative(self):
        """Test the margin when sale price is less then cost"""
        blanket_order = self.blanket_order_obj.create(
            {
                "partner_id": self.partner.id,
                "validity_date": fields.Date.to_string(self.tomorrow),
                "payment_term_id": self.payment_term.id,
                "pricelist_id": self.sale_pricelist.id,
            }
        )
        blanket_order.sudo().onchange_partner_id()
        blanket_order.write(
            {
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Blanket line Demo 1",
                            "product_id": self.product.id,
                            "product_uom": self.product.uom_id.id,
                            "purchase_price": 40.0,
                            "original_uom_qty": 1.0,
                            "price_unit": 20.0,
                        },
                    ),
                ],
            }
        )
        blanket_order.sudo().action_confirm()
        self.assertEqual(blanket_order.line_ids[0].margin, -20.00)
        self.assertEqual(blanket_order.line_ids[0].margin_percent, -1.00)
        self.assertEqual(blanket_order.margin, -20.00)
        self.assertEqual(blanket_order.margin_percent, -1.0)
