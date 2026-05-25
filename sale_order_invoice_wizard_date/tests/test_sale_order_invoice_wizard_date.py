# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestSaleOrderInvoiceWizardDate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "service",
                "invoice_policy": "order",
                "list_price": 100.0,
            }
        )

    def _create_confirmed_order(self):
        order = self.env["sale.order"].create(
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
        order.action_confirm()
        return order

    def _invoice_order(self, order, invoice_date=None):
        wizard = (
            self.env["sale.advance.payment.inv"]
            .with_context(active_ids=order.ids, active_model="sale.order")
            .create(
                {
                    "advance_payment_method": "delivered",
                    "invoice_date": invoice_date,
                }
            )
        )
        wizard.create_invoices()
        return order.invoice_ids

    def test_invoice_date_is_set_on_invoice(self):
        """Wizard invoice_date must be copied to the generated invoice."""
        order = self._create_confirmed_order()
        target_date = date(2025, 6, 15)

        invoices = self._invoice_order(order, invoice_date=target_date)

        self.assertTrue(invoices, "No invoice was created")
        self.assertEqual(invoices[0].invoice_date, target_date)

    def test_invoice_date_propagates_to_multiple_orders(self):
        """All invoices generated from multiple orders must share the wizard date."""
        order1 = self._create_confirmed_order()
        order2 = self._create_confirmed_order()
        target_date = date(2025, 9, 30)

        wizard = (
            self.env["sale.advance.payment.inv"]
            .with_context(
                active_ids=(order1 + order2).ids,
                active_model="sale.order",
            )
            .create(
                {
                    "advance_payment_method": "delivered",
                    "invoice_date": target_date,
                }
            )
        )
        wizard.create_invoices()

        for order in (order1, order2):
            self.assertTrue(order.invoice_ids, f"No invoice for order {order.name}")
            self.assertEqual(order.invoice_ids[0].invoice_date, target_date)
