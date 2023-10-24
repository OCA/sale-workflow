from odoo.tests import Form, tagged

from odoo.addons.stock_available_to_promise_release.tests.common import (
    PromiseReleaseCommonCase,
)


@tagged("post_install", "-at_install")
class TestStockReserveSale(PromiseReleaseCommonCase):
    def setUp(self):
        super().setUp()
        self.wh.delivery_route_id.write({"available_to_promise_defer_pull": True})

    def test_ordered_available_to_promise_value_base(self):
        self._update_qty_in_location(self.loc_bin1, self.product1, 18.0)
        picking1 = self._out_picking(
            self._create_picking_chain(
                self.wh,
                [(self.product1, 5)],
            )
        )
        picking2 = self._out_picking(
            self._create_picking_chain(
                self.wh,
                [(self.product1, 5)],
            )
        )
        partner_form = Form(self.env["res.partner"])
        partner_form.name = "Test partner"
        self.partner = partner_form.save()
        sale_order_form = Form(self.env["sale.order"])
        sale_order_form.partner_id = self.partner
        with sale_order_form.order_line.new() as order_line_form:
            order_line_form.product_id = self.product1
            order_line_form.product_uom_qty = 5
        sale = sale_order_form.save()
        sale.warehouse_id = self.wh
        sale.reserve_stock()
        picking3 = self._out_picking(
            self._create_picking_chain(
                self.wh,
                [(self.product1, 5)],
            )
        )
        self.assertEqual(picking1.move_lines.previous_promised_qty, 0)
        self.assertEqual(picking1.move_lines.ordered_available_to_promise_uom_qty, 5)
        self.assertEqual(picking2.move_lines.previous_promised_qty, 5)
        self.assertEqual(picking2.move_lines.ordered_available_to_promise_uom_qty, 5)
        self.assertEqual(picking3.move_lines.previous_promised_qty, 15)
        self.assertEqual(picking3.move_lines.ordered_available_to_promise_uom_qty, 3)
        sale.action_confirm()
        self.assertEqual(picking1.move_lines.previous_promised_qty, 0)
        self.assertEqual(picking1.move_lines.ordered_available_to_promise_uom_qty, 5)
        self.assertEqual(picking2.move_lines.previous_promised_qty, 5)
        self.assertEqual(picking2.move_lines.ordered_available_to_promise_uom_qty, 5)
        self.assertEqual(sale.picking_ids.move_lines.previous_promised_qty, 10)
        self.assertEqual(
            sale.picking_ids.move_lines.ordered_available_to_promise_uom_qty, 5
        )
        self.assertEqual(picking3.move_lines.previous_promised_qty, 15)
        self.assertEqual(picking3.move_lines.ordered_available_to_promise_uom_qty, 3)
