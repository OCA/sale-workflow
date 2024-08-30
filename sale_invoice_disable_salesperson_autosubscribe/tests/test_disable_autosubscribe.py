# Copyright 2024 Roger Sans <roger.sans@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo import fields
from odoo.fields import Command
from odoo.tests import tagged

from odoo.addons.sale.tests.common import TestSaleCommon

_logger = logging.getLogger(__name__)


@tagged("-at_install", "post_install")
class TestDisableAutosubscribe(TestSaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_user = cls.env.ref("base.user_demo")
        cls.test_company = cls.test_user.company_id
        cls.test_partner = cls.env.ref("base.res_partner_1")
        cls.test_product = cls.env.ref("product.consu_delivery_01")

    @classmethod
    def _get_taxes(cls, descs):
        taxes = cls.env["account.tax"]
        for desc in descs.split(","):
            parts = desc.split(".")
            xml_id = parts[1] if len(parts) > 1 else parts[0]
            if xml_id.lower() != xml_id and len(parts) == 1:
                # shortcut for not changing existing tests with old codes
                xml_id = "account_tax_template_" + xml_id.lower()
            tax_id = cls.company._get_tax_id_from_xmlid(xml_id)
            taxes |= cls.env["account.tax"].browse(tax_id)
            if not tax_id:
                _logger.error(f"Tax not found: {desc}")
        return taxes

    def test_subscribed(self):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.test_partner.id,
                "user_id": self.test_user.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.test_product.id,
                            "product_uom_qty": 2,
                            "price_unit": 223.4,
                        }
                    )
                ],
            }
        )

        context = {
            "active_model": "sale.order",
            "active_ids": [sale_order.id],
            "active_id": sale_order.id,
            "default_journal_id": self.company_data["default_journal_sale"].id,
            "default_invoice_user_id": self.test_user.id,
        }

        sale_order.action_confirm()
        payment = (
            self.env["sale.advance.payment.inv"].with_context(**context).create({})
        )
        payment.create_invoices()
        invoice = sale_order.invoice_ids[0]
        actual_followers = invoice.message_follower_ids.ids
        self.assertFalse(invoice.invoice_user_id.id in actual_followers)

        direct_invoice = self.env["account.move"].create(
            [
                {
                    "move_type": "out_invoice",
                    "partner_id": self.test_partner.id,
                    "invoice_date": fields.Date.from_string("2016-01-01"),
                    "currency_id": self.currency_data["currency"].id,
                    "invoice_user_id": self.test_user.id,
                    "invoice_line_ids": [
                        (
                            0,
                            None,
                            {
                                "product_id": self.test_product.id,
                                "quantity": 3,
                                "price_unit": 750,
                            },
                        ),
                    ],
                }
            ]
        )

        direct_followers = invoice.message_follower_ids.ids
        self.assertFalse(direct_invoice.invoice_user_id.id in direct_followers)
