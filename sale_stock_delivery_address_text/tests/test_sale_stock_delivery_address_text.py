# Copyright 2026 Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import Command
from odoo.tests import TransactionCase


class TestSaleStockDeliveryAddressText(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.address = "Morelos St. 123, Downtown, blue gate"
        cls.partner = cls.env["res.partner"].create({"name": "Generic Customer"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "is_storable": True}
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "delivery_address_text": cls.address,
                "order_line": [
                    Command.create({"product_id": cls.product.id, "product_uom_qty": 1})
                ],
            }
        )

    def test_01_address_propagates_to_picking(self):
        self.order.action_confirm()
        picking = self.order.picking_ids
        self.assertTrue(picking)
        self.assertEqual(picking.delivery_address_text, self.address)
        new_address = "New address 456"
        self.order.delivery_address_text = new_address
        self.assertEqual(picking.delivery_address_text, new_address)

    def test_02_address_printed_on_reports(self):
        self.order.action_confirm()
        picking = self.order.picking_ids
        for report in ("stock.action_report_delivery", "stock.action_report_picking"):
            html = self.env["ir.actions.report"]._render_qweb_html(report, picking.ids)[
                0
            ]
            self.assertIn(self.address.encode(), html)
