# Copyright 2026 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo.addons.base.tests.common import BaseCommon


class TestProductCustomerInfoSale(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_invoice_alone = cls.env["product.product"].create(
            {
                "name": "Product invoice alone",
                "type": "consu",
                "invoice_policy": "delivery",
            }
        )
        cls.product_not_invoice_alone = cls.env["product.product"].create(
            {
                "name": "Product not invoice alone",
                "type": "service",
                "invoice_policy": "order",
                "avoid_invoice_alone": True,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.sale = cls.env["sale.order"].create({"partner_id": cls.partner.id})

    def test_01_invoice_status_no(self):
        self.env["sale.order.line"].create(
            [
                {
                    "order_id": self.sale.id,
                    "product_id": self.product_invoice_alone.id,
                    "product_uom_qty": 1.0,
                },
                {
                    "order_id": self.sale.id,
                    "product_id": self.product_not_invoice_alone.id,
                    "product_uom_qty": 1.0,
                },
            ]
        )
        self.sale.action_confirm()
        self.assertEqual(self.sale.invoice_status, "no")

    def test_01_invoice_status_to_invoice(self):
        self.product_not_invoice_alone.avoid_invoice_alone = False
        self.env["sale.order.line"].create(
            [
                {
                    "order_id": self.sale.id,
                    "product_id": self.product_invoice_alone.id,
                    "product_uom_qty": 1.0,
                },
                {
                    "order_id": self.sale.id,
                    "product_id": self.product_not_invoice_alone.id,
                    "product_uom_qty": 1.0,
                },
            ]
        )
        self.sale.action_confirm()
        self.assertEqual(self.sale.invoice_status, "to invoice")
