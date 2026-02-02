# Copyright 2023 ACSONE SA/NV
# Copyright 2025 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import TestSaleOrderLineCancelBase


class TestSaleOrderLineCancel(TestSaleOrderLineCancelBase):
    def test_cancel_remaining_qty(self):
        line = self.sale.order_line
        self.assertEqual(line.product_qty_remains_to_deliver, 10)
        self.assertEqual(line.product_qty_canceled, 0)
        self.wiz.with_context(
            active_id=line.id, active_model="sale.order.line"
        ).cancel_remaining_qty()
        self.assertEqual(line.product_qty_remains_to_deliver, 0)
        self.assertEqual(line.product_qty_canceled, 10)

    def test_reset_to_draft(self):
        self.sale.order_line.cancel_remaining_qty()
        self.assertEqual(self.sale.order_line.product_qty_canceled, 10)
        self.assertEqual(self.sale.order_line.product_qty_remains_to_deliver, 0)
        self.sale.with_context(disable_cancel_warning=True).action_cancel()
        self.assertEqual(self.sale.order_line.product_qty_canceled, 10)
        self.assertEqual(self.sale.order_line.product_qty_remains_to_deliver, 0)
        self.sale.action_draft()
        self.assertEqual(self.sale.order_line.product_qty_canceled, 0)
        self.assertEqual(self.sale.order_line.product_qty_remains_to_deliver, 10)

    def test_cancel_decrease_product_uom_qty(self):
        sale = self.sale
        line = sale.order_line
        sale.company_id.on_sale_line_cancel_decrease_line_qty = True
        sale.with_context(disable_cancel_warning=True).action_cancel()
        sale.action_draft()
        sale.action_confirm()
        line.cancel_remaining_qty()
        self.assertEqual(line.product_qty_canceled, 10)
        self.assertEqual(line.product_qty_remains_to_deliver, 0)
        self.assertEqual(line.qty_delivered, 0)
        self.assertEqual(line.product_uom_qty, 0)

    def test_ensure_no_decrease_product_uom_qty_on_so_cancel(self):
        sale = self.sale
        line = sale.order_line
        sale.with_context(disable_cancel_warning=True).action_cancel()
        sale.company_id.on_sale_line_cancel_decrease_line_qty = True
        sale.action_cancel()
        self.assertEqual(sale.order_line.product_uom_qty, 10)
        self.assertEqual(line.product_qty_canceled, 0)
