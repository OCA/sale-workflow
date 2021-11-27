# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class TestSaleAmountPaymentLink(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.company_data["company"].country_id = cls.env.ref("base.us")

        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner_a.id,
                "order_line": [
                    (
                        0,
                        False,
                        {
                            "product_id": cls.product_a.id,
                            "name": "1 Product",
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )
        cls.env.ref("payment.payment_acquirer_transfer").journal_id = cls.company_data[
            "default_journal_cash"
        ]

        cls.transaction = cls.order._create_payment_transaction(
            {"acquirer_id": cls.env.ref("payment.payment_acquirer_transfer").id}
        )

    def test_sale_reduce_amount(self):
        """Test the following scenario:
        - Create a sale order
        - Create a transaction for the sale order.
        - Confirm the transaction.
        - Add more products to Order Lines.
        => The Amount on Generate Payment Link wizard must be reduced accordingly.
        """
        self.transaction._set_transaction_done()
        self.transaction._post_process_after_done()
        self.order.write(
            {
                "order_line": [
                    (
                        0,
                        False,
                        {
                            "product_id": self.product_a.id,
                            "name": "1 Product",
                            "price_unit": 100.0,
                        },
                    )
                ]
            }
        )
        ctx = {"active_model": "sale.order", "active_id": self.order.id}
        f = Form(self.env["payment.link.wizard"].with_context(ctx))
        # this should be amount reduced with amount already paid by transaction
        self.assertEqual(f.amount, 115)
