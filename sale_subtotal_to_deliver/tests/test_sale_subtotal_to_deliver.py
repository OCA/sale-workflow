# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo.fields import Datetime
from odoo.tests.common import TransactionCase


class TestSaleSubtotalToDeliver(TransactionCase):
    def setUp(self):
        super(TestSaleSubtotalToDeliver, self).setUp()
        self.sale_order_model = self.env["sale.order"]
        self.sale_order_line_model = self.env["sale.order.line"]
        partner_model = self.env["res.partner"]
        prod_model = self.env["product.product"]
        uom_id = prod_model.uom_id.search([("name", "=", "Units")], limit=1).id

        partner = {"name": "Partner 1"}
        self.partner_prueba = partner_model.sudo().create(partner)

        partner_2 = {"name": "Partner 2"}
        self.partner_prueba_2 = partner_model.sudo().create(partner_2)

        so1 = {
            "partner_id": self.partner_prueba.id,
            "date_order": Datetime.now(),
        }
        self.so1_prueba = self.sale_order_model.sudo().create(so1)

        pr_1 = {
            "name": "Product Test 1",
            "uom_id": uom_id,
        }
        self.product_1 = prod_model.sudo().create(pr_1)

        commitment_date = Datetime.now() + timedelta(days=7)

        self.tax_prueba = self.env["account.tax"].create(
            {
                "name": "tax_prueba",
                "amount_type": "percent",
                "amount": 20,
                "price_include": True,
                "include_base_amount": False,
            }
        )
        so_line_1 = {
            "product_id": self.product_1.id,
            "name": "SO_PRUEBA001",
            "product_uom_qty": 10.0,
            "price_unit": 10.0,
            "order_id": self.so1_prueba.id,
            "commitment_date": commitment_date,
            "tax_id": self.tax_prueba,
        }
        self.soline_1 = self.sale_order_line_model.sudo().create(so_line_1)
        self.so1_prueba._action_confirm()

    def test_01_compute_subtotal_qty_delivered_and_to_deliver(self):

        self.subtotal_to_deliver_ini = self.soline_1.subtotal_to_deliver
        self.subtotal_delivered_ini = self.soline_1.subtotal_delivered

        self.assertEqual(
            self.subtotal_delivered_ini + self.subtotal_to_deliver_ini,
            self.soline_1.price_subtotal,
        )

        self.assertEqual(self.soline_1.qty_delivered, 0.0)
        self.assertEqual(self.soline_1.qty_to_deliver, 10.0)
        self.soline_1.qty_delivered = 5.0
        self.assertEqual(self.soline_1.qty_delivered, 5.0)
        self.assertEqual(self.soline_1.qty_to_deliver, 5.0)

        self.subtotal_to_deliver = self.soline_1.subtotal_to_deliver
        self.subtotal_delivered = self.soline_1.subtotal_delivered
        self.assertNotEqual(self.subtotal_delivered, self.subtotal_delivered_ini)
        self.assertNotEqual(self.subtotal_to_deliver, self.subtotal_to_deliver_ini)

        self.assertEqual(
            round(self.subtotal_delivered + self.subtotal_to_deliver, 1),
            round(self.soline_1.price_subtotal, 1),
        )
