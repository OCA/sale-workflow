# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from freezegun import freeze_time

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
        with freeze_time("2024-05-30"):
            picking1 = self._out_picking(
                self._create_picking_chain(
                    self.wh,
                    [(self.product1, 5)],
                )
            )
        with freeze_time("2024-05-31"):
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
        with freeze_time("2024-06-01"):
            sale.reserve_stock()
        with freeze_time("2024-06-02"):
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
        date_priority = sale.picking_ids.move_lines.date_priority
        sale.action_confirm()
        date_priority_new = sale.picking_ids.move_lines.date_priority
        self.assertEqual(date_priority, date_priority_new)
        self.assertTrue(date_priority < picking3.move_lines.date_priority)
        self.assertEqual(picking1.move_lines.previous_promised_qty, 0)
        self.assertEqual(picking1.move_lines.ordered_available_to_promise_uom_qty, 5)
        self.assertEqual(picking2.move_lines.previous_promised_qty, 5)
        self.assertEqual(picking2.move_lines.ordered_available_to_promise_uom_qty, 5)
        self.assertEqual(picking3.move_lines.previous_promised_qty, 15)
        self.assertEqual(picking3.move_lines.ordered_available_to_promise_uom_qty, 3)
        self.assertEqual(sale.picking_ids.move_lines.previous_promised_qty, 10)
        self.assertEqual(
            sale.picking_ids.move_lines.ordered_available_to_promise_uom_qty, 5
        )
