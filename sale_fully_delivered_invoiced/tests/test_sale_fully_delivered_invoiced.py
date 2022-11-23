# Copyright 2022 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import common, tagged


@tagged("-at_install", "post_install")
class TestSaleFullyDeliveredInvoiced(common.TransactionCase):
    def setUp(self):
        super().setUp()

        # ENVIRONMENTS
        self.sale_order = self.env["sale.order"]
        self.partner_id = self.env.ref("base.res_partner_1")
        self.product_id_1 = self.env.ref("product.product_product_8")
        self.account_model = self.env["account.account"]
        self.product_id_1.write({"invoice_policy": "order"})
        self.env["stock.quant"].create(
            {
                "product_id": self.product_id_1.id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "quantity": 40.0,
            }
        )
        self.so_vals = {
            "partner_id": self.partner_id.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": self.product_id_1.name,
                        "product_id": self.product_id_1.id,
                        "product_uom_qty": 5.0,
                        "product_uom": self.product_id_1.uom_po_id.id,
                        "price_unit": 500.0,
                    },
                ),
            ],
        }
        self.so = self.sale_order.create(self.so_vals)
        self.currency_eur = self.env.ref("base.EUR")
        self.supplier = self.env["res.partner"].create({"name": "Test supplier"})

    def test_00_sale_order_not_delivered(self):
        """
        The SO is not even delivered. Should not be closed
        """
        self.so.action_confirm()
        self.assertFalse(self.so.is_fully_delivered)
        self.assertEqual(self.so.invoice_status_validated, "to invoice")

    def test_01_sale_order_delivered_not_invoiced(self):
        """If not invoiced it should not be auto closed"""
        self.so.action_confirm()
        picking = self.so.picking_ids
        picking.action_assign()
        for move in picking.move_lines.filtered(lambda m: m.state != "waiting"):
            move.quantity_done = move.product_qty
        picking.button_validate()
        self.assertEqual(
            self.so.order_line[0].product_uom_qty,
            self.so.order_line[0].qty_delivered,
            "The product quantity and the product delivered should be the same",
        )
        self.assertTrue(self.so.is_fully_delivered)
        self.assertEqual(self.so.invoice_status_validated, "to invoice")

    def test_02_sale_order_delivered_invoiced_not_posted(self):
        """If the invoice is not posted is the same thing"""
        self.so.action_confirm()
        picking = self.so.picking_ids
        picking.action_assign()
        for move in picking.move_lines.filtered(lambda m: m.state != "waiting"):
            move.quantity_done = move.product_qty
        picking.button_validate()
        self.so._create_invoices()
        self.assertTrue(self.so.is_fully_delivered)
        self.assertEqual(self.so.invoice_status_validated, "to invoice")

    def test_03_sale_order_delivered_invoiced_posted(self):
        """
        If invoiced and validated then it should close the SO
        """
        self.so.action_confirm()
        picking = self.so.picking_ids
        picking.action_assign()
        for move in picking.move_lines.filtered(lambda m: m.state != "waiting"):
            move.quantity_done = move.product_qty
        picking.button_validate()
        self.so._create_invoices()
        self.so.invoice_ids.post()
        self.assertTrue(self.so.is_fully_delivered)
        self.assertEqual(self.so.invoice_status_validated, "invoiced")
