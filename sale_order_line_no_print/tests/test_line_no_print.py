# Copyright 2026 Moduon Team SL
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo.tests import Form

from odoo.addons.sale.tests.common import TestSaleCommon


class TestLineNoPrint(TestSaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner_a.id,
            }
        )

    def test_sale_order_line_display_in_report_default(self):
        """Test that display_in_report field defaults to True."""
        for line in self.sale_order.order_line:
            self.assertTrue(line.display_in_report)

    def test_sale_order_line_display_in_report_cannot_set_to_false(self):
        """Test display_in_report cannot be set to False on priced lines in the UI."""
        with Form(self.sale_order) as order_form:
            # Check that display_in_report is not visible/writable if price_total != 0.0
            with self.assertRaisesRegex(Exception, "display_in_report"):
                with order_form.order_line.new() as sol:
                    sol.product_id = self.service_product
                    sol.product_uom_qty = 1.0
                    sol.price_unit = 100.0
                    sol.tax_ids.clear()  # Remove taxes to avoid complexity in the test
                    self.assertEqual(sol.price_total, 100.0)
                    self.assertTrue(sol.display_in_report)
                    sol.display_in_report = False

    def test_sale_order_line_display_in_report_can_set_to_false(self):
        """Test display_in_report can be set to False on priced lines in the UI."""
        with Form(self.sale_order) as order_form:
            # Check that display_in_report is visible/writable if price_total = 0.0
            with order_form.order_line.new() as sol:
                sol.product_id = self.service_product
                sol.product_uom_qty = 0.0
                self.assertEqual(sol.price_total, 0.0)
                self.assertTrue(sol.display_in_report)
                sol.display_in_report = False
                self.assertFalse(sol.display_in_report)

    def test_display_in_report_propagation_and_report_selection(self):
        """Test that display_in_report is propagated to invoice lines
        and lines to report are selected appropriately."""
        # Create sale order and invoice
        with Form(self.sale_order) as order_form:
            with order_form.order_line.new() as sol:
                sol.product_id = self.service_product
                sol.product_uom_qty = 0.0
                sol.display_in_report = False
            with order_form.order_line.new() as sol:
                sol.product_id = self.service_product
                sol.product_uom_qty = 1.0
                sol.price_unit = 100.0
                sol.tax_ids.clear()
        self.sale_order.action_confirm()
        self.sale_order._create_invoices()
        # Check lines to report on sale order
        lines_to_report = self.sale_order._get_order_lines_to_report()
        self.assertEqual(len(lines_to_report), 1)
        self.assertTrue(lines_to_report.display_in_report)
        # Check propagation to invoice and lines to report on invoice
        lines_to_report = self.sale_order.invoice_ids._get_move_lines_to_report()
        self.assertEqual(len(lines_to_report), 1)
        self.assertTrue(lines_to_report.display_in_report)
