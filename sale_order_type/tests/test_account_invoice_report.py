from odoo import fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountInvoiceReport(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        # Remove this variable in v16 and put instead:
        # from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
        DISABLED_MAIL_CONTEXT = {
            "tracking_disable": True,
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.sale_order_types = cls.env["sale.order.type"].create(
            [
                {
                    "name": "Normal Order",
                },
                {
                    "name": "Special Order",
                },
            ]
        )

        cls.invoices = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.partner_a.id,
                "invoice_date": fields.Date.from_string("2021-01-01"),
                "sale_type_id": cls.sale_order_types[0].id,  # Normal Order
                "currency_id": cls.currency_data["currency"].id,
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
        self.env["account.invoice.report"].read_group(
            domain=[],
            fields=["product_id, quantity, sale_type_id"],
            groupby="sale_type_id",
        )
