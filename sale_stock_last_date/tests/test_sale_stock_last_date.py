# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form, TransactionCase


class TestSaleStockLastDate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.product = cls.env["product.product"].create(
            {"name": "test", "type": "consu", "is_storable": True}
        )
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "quantity": 2000,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "test - partner"})
        order_form = Form(cls.env["sale.order"])
        order_form.partner_id = cls.partner
        with order_form.order_line.new() as line_form:
            line_form.product_id = cls.product
            line_form.product_uom_qty = 10
            line_form.price_unit = 1000
        cls.order = order_form.save()

    def _return_whole_picking(self, picking, to_refund=True):
        """Helper method to create a return of the original picking. It could
        be refundable or not"""
        return_wiz_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=picking.ids,
                active_id=picking.ids[0],
                active_model="stock.picking",
            )
        )
        return_wiz = return_wiz_form.save()
        return_wiz.product_return_moves.quantity = picking.move_ids[0].quantity
        return_wiz.product_return_moves.to_refund = to_refund
        res = return_wiz.action_create_returns()
        return_picking = self.env["stock.picking"].browse(res["res_id"])
        self._validate_picking(return_picking)

    def _validate_picking(self, picking):
        """Helper method to confirm the pickings"""
        for line in picking.move_ids:
            line.write({"quantity": line.product_uom_qty, "picked": True})
        picking.move_ids._action_done()

    def test_last_delivery_date(self):
        self.order.action_confirm()
        self.assertFalse(self.order.order_line.last_delivery_date)
        # Partial delivery one
        picking = self.order.picking_ids
        picking.action_assign()
        # Set the quantity_done and mark move as done directly
        picking.move_ids.write({"quantity": 2.0, "picked": True})
        picking.move_ids._action_done()
        # Discard any so line like as delivery line for tests in travis
        so_line = self.order.order_line.filtered(
            lambda ln: ln.product_id == self.product
        )
        self.assertEqual(so_line.last_delivery_date, picking.move_ids.date)
        # Partial delivery two
        backorder = self.order.picking_ids.filtered(lambda p: p.state != "done")
        backorder.action_assign()
        # Set the quantity_done and mark move as done directly
        backorder.move_ids.write({"quantity": 2.0, "picked": True})
        backorder.move_ids._action_done()
        self.assertEqual(so_line.last_delivery_date, backorder.move_ids.date)
        # Make a return. This movement does not affect
        self._return_whole_picking(picking, to_refund=True)
        self.assertEqual(so_line.last_delivery_date, backorder.move_ids.date)
