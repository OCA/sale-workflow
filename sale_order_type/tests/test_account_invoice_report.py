from odoo import fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountInvoiceReport(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.other_currency = cls.setup_other_currency("ARS")
        cls.sale_order_types = (
            cls.env["sale.order.type"]
            .sudo()
            .create(
                [
                    {
                        "name": "Normal Order",
                    },
                    {
                        "name": "Special Order",
                    },
                ]
            )
        )

        cls.invoices = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.partner_a.id,
                "invoice_date": fields.Date.from_string("2021-01-01"),
                "sale_type_id": cls.sale_order_types[0].id,  # Normal Order
                "currency_id": cls.other_currency.id,
                "invoice_line_ids": [
                    (
                        0,
                        None,
                        {
                            "product_id": cls.product_a.id,
                            "quantity": 3,
                            "price_unit": 750,
                        },
                    ),
                    (
                        0,
                        None,
                        {
                            "product_id": cls.product_a.id,
                            "quantity": 1,
                            "price_unit": 3000,
                        },
                    ),
                ],
            }
        )

    def test_invoice_report_sale_order_type(self):
        self.env["account.invoice.report"]._read_group(
            domain=[],
            groupby=["sale_type_id"],
            aggregates=["product_id:recordset", "quantity:sum"],
        )
