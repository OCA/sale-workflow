# Copyright 2022 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import common, tagged


@tagged("-at_install", "post_install")
class TestSaleFullyDeliveredInvoiced(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # ENVIRONMENTS
        cls.sale_order = cls.env["sale.order"]
        cls.partner_id = cls.env.ref("base.res_partner_1")
        cls.product_id_1 = cls.env.ref("product.product_product_8")
        cls.account_model = cls.env["account.account"]
        cls.product_id_1.write({"invoice_policy": "order"})
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product_id_1.id,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "quantity": 40.0,
            }
        )
        cls.so_vals = {
            "partner_id": cls.partner_id.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": cls.product_id_1.name,
                        "product_id": cls.product_id_1.id,
                        "product_uom_qty": 5.0,
                        "product_uom": cls.product_id_1.uom_po_id.id,
                        "price_unit": 500.0,
                    },
                ),
            ],
        }
        cls.so = cls.sale_order.create(cls.so_vals)
        cls.currency_eur = cls.env.ref("base.EUR")
        cls.supplier = cls.env["res.partner"].create({"name": "Test supplier"})

    def test_00_sale_order_not_delivered(self):
        """
        The SO is not even delivered. Should not be closed
        """
        self.so.action_confirm()
        self.assertFalse(self.so.is_fully_delivered)

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
        self.so.invoice_ids._post()
        self.assertTrue(self.so.is_fully_delivered)
