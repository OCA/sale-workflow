# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import common


class TestSaleOrderSerialAccount(common.TransactionCase):
    def test_sale_order_serial_account(self):
        partner_1 = self.env["res.partner"].create({"name": "Test partner1"})
        product1 = self.env["product.product"].create(
            {"name": "TestProduct", "tracking": "serial",
             "invoice_policy": "order"}
        )

        sale_order = self.env["sale.order"].create(
            {
                "partner_id": partner_1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product1.id,
                            "serial_sequence_id": self.env.ref(
                                "stock.sequence_production_lots"
                            ).id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )
        sale_order.action_fill_serials()
        sale_order.action_confirm()
        sale_order._create_invoices()
        self.assertTrue(sale_order.invoice_ids.invoice_line_ids[0].serial_list)
