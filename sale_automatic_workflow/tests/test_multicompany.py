# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import tagged

from .common import TestMultiCompanyCommon


@tagged("post_install", "-at_install")
class TestMultiCompany(TestMultiCompanyCommon):
    """Class to test sale automated workflow with multi-company."""

    def test_sale_order_multicompany(self):
        self.env.user.company_id = self.env.ref("base.main_company")
        order_fr = self.create_auto_wkf_order(
            self.company_fr, self.customer_fr, self.product_fr, 5
        )
        order_ch = self.create_auto_wkf_order(
            self.company_ch, self.customer_ch, self.product_ch, 10
        )
        order_be = self.create_auto_wkf_order(
            self.company_be, self.customer_be, self.product_be, 10
        )
        order_fr_daughter = self.create_auto_wkf_order(
            self.company_fr_daughter,
            self.customer_fr_daughter,
            self.product_fr_daughter,
            4,
        )

        self.assertEqual(order_fr.state, "draft")
        self.assertEqual(order_ch.state, "draft")
        self.assertEqual(order_be.state, "draft")
        self.assertEqual(order_fr_daughter.state, "draft")

        self.env["automatic.workflow.job"].run()
        invoice_fr = order_fr.invoice_ids
        invoice_ch = order_ch.invoice_ids
        invoice_be = order_be.invoice_ids
        invoice_fr_daughter = order_fr_daughter.invoice_ids
        self.assertEqual(invoice_fr.state, "posted")
        self.assertEqual(invoice_fr.journal_id.company_id, order_fr.company_id)
        self.assertEqual(invoice_ch.state, "posted")
        self.assertEqual(invoice_ch.journal_id.company_id, order_ch.company_id)
        self.assertEqual(invoice_be.state, "posted")
        self.assertEqual(invoice_be.journal_id.company_id, order_be.company_id)
        self.assertEqual(invoice_fr_daughter.state, "posted")
        self.assertEqual(
            invoice_fr_daughter.journal_id.company_id, order_fr_daughter.company_id
        )

        # Test payment register
        self.auto_wkf.register_payment = True
        self.env["automatic.workflow.job"].run()
        self.assertIn(invoice_fr.payment_state, ["in_payment", "paid"])
        self.assertIn(invoice_ch.payment_state, ["in_payment", "paid"])
        self.assertIn(invoice_be.payment_state, ["in_payment", "paid"])
        self.assertIn(invoice_fr_daughter.payment_state, ["in_payment", "paid"])
        # Check payment journal company matches the order company
        payment_fr = invoice_fr.matched_payment_ids
        payment_ch = invoice_ch.matched_payment_ids
        payment_be = invoice_be.matched_payment_ids
        payment_fr_daughter = invoice_fr_daughter.matched_payment_ids
        self.assertEqual(payment_fr.journal_id.company_id, order_fr.company_id)
        self.assertEqual(payment_ch.journal_id.company_id, order_ch.company_id)
        self.assertEqual(payment_be.journal_id.company_id, order_be.company_id)
        self.assertEqual(
            payment_fr_daughter.journal_id.company_id, order_fr_daughter.company_id
        )
