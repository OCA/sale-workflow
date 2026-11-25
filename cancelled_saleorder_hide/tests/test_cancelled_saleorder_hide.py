# Copyright 2026 M. Salman
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase, tagged
from odoo.tools.safe_eval import safe_eval


@tagged("post_install", "-at_install")
class TestCancelledSaleorderHide(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "type": "consu", "list_price": 100.0}
        )

    def _create_sale_order(self):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )

    def test_sale_order_action_domain_hides_cancelled(self):
        """Cancelled sale orders must not match the Quotations action domain."""
        active_order = self._create_sale_order()
        cancelled_order = self._create_sale_order()
        # Force the cancel state directly: we are testing the view domain,
        # not the cancellation workflow itself.
        cancelled_order.write({"state": "cancel"})

        action = self.env.ref("sale.action_quotations_with_onboarding")
        domain = action.domain
        orders = self.env["sale.order"].search(
            safe_eval(domain) + [("id", "in", (active_order.id, cancelled_order.id))]
        )

        self.assertIn(active_order, orders)
        self.assertNotIn(cancelled_order, orders)

    def test_invoice_action_domain_hides_cancelled_sale_order_invoices(self):
        """Invoices linked to a cancelled sale order must not match the
        Customer Invoices action domain, while unrelated invoices remain."""
        order = self._create_sale_order()
        order.action_confirm()
        invoice = order._create_invoices()
        unrelated_invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "quantity": 1,
                            "price_unit": 50.0,
                        },
                    )
                ],
            }
        )

        # Force-cancel the sale order to test the domain in isolation.
        order.write({"state": "cancel"})

        action = self.env.ref("account.action_move_out_invoice_type")
        domain = action.domain
        moves = self.env["account.move"].search(
            safe_eval(domain) + [("id", "in", (invoice.id, unrelated_invoice.id))]
        )

        self.assertNotIn(invoice, moves)
        self.assertIn(unrelated_invoice, moves)
