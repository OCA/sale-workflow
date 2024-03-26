# Copyright 2023 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.sale_order_revision.tests import test_sale_order_revision


class TestSaleOrderRevisionStock(test_sale_order_revision.TestSaleOrderRevision):
    def test_revision_keeps_stock(self):
        sale = self._create_tester()
        sale.action_confirm()
        self._create_sale_invoice(sale)
        sale.action_cancel_create_revision()
        self.assertEqual(
            sale.current_revision_id.picking_ids,
            sale.picking_ids,
            "The Sale Order revision keeps a link to the original Stock Moves",
        )
