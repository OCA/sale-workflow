# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSaleInvoiceNoMail(TransactionCase):
    def test_00_invoice_without_mail(self):
        partner = self.env["res.partner"].create({"name": "Test Partner"})
        product = self.env["product.product"].create(
            {"name": "Test Product", "invoice_policy": "order"}
        )
        sale = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_qty": 5,
                            "price_unit": 10,
                        },
                    )
                ],
            }
        )
        sale.action_confirm()
        old_mails = self.env["mail.mail"].sudo().search([])
        wiz = self.env["sale.advance.payment.inv"]
        wiz = wiz.with_context(active_ids=sale.ids)
        wiz = wiz.create({"advance_payment_method": "delivered"})
        wiz.create_invoices()
        new_mails = self.env["mail.mail"].sudo().search([]) - old_mails
        self.assertFalse(new_mails)
