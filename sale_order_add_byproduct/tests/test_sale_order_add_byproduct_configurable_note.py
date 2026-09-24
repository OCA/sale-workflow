# © 2025 OBS Solutions
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .test_sale_order_add_byproduct import TestByproductToSaleOrder


class TestByproductToSaleOrderConfigurableNote(TestByproductToSaleOrder):
    def test_07_byproduct_added_with_custom_note(self):
        """
        Test that a new by-product line is added to the SO with a custom note.
        """
        # Set a custom note template on the company
        custom_template = "Custom note for {product_name} from {mo_name}"
        self.env.company.byproduct_note_template = custom_template

        mo, sale_order = self._create_and_process_mo_for_sale_order(
            main_product_qty=1.0, byproduct_produced_qty=0.5
        )

        # Mark MO as done
        mo.button_mark_done()

        # Assert MO is done
        self.assertEqual(
            mo.state, "done", "Manufacturing order should be in 'done' state."
        )

        # Assert a new sale order line for the byproduct is created
        byproduct_so_line = sale_order.order_line.filtered(
            lambda li: li.product_id == self.product_byproduct
            and li.is_mrp_byproduct_line
        )
        self.assertTrue(
            byproduct_so_line,
            "By-product line was not added to the Sale Order.",
        )

        # Refresh the record to get the latest data
        byproduct_so_line.invalidate_recordset()
        byproduct_so_line = self.env["sale.order.line"].browse(byproduct_so_line.id)

        expected_note = custom_template.format(
            product_name=self.product_byproduct.name, mo_name=mo.name
        )
        self.assertEqual(
            byproduct_so_line.name,
            expected_note,
            "By-product line note is not the expected custom note.",
        )
