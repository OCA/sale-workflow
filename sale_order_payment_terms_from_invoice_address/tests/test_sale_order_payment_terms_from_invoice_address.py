# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestSaleOrderPaymentTerms(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Partner A",
                "property_payment_term_id": cls.env["account.payment.term"]
                .create(
                    {
                        "name": "Payment Term Partner A",
                    }
                )
                .id,
            }
        )
        cls.partner_invoice = cls.env["res.partner"].create(
            {
                "name": "Partner B",
                "property_payment_term_id": cls.env["account.payment.term"]
                .create(
                    {
                        "name": "Payment Term Partner B",
                    }
                )
                .id,
            }
        )
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner_invoice.id,
            }
        )
        cls.setting_name = (
            "sale_order_payment_terms_from_invoice_address."
            + "compute_so_payment_terms_from_partner_invoice"
        )

    def test_payment_terms_from_partner(self):
        """
        Test that payment terms are computed from partner_id
        when the option is not checked.
        """
        self.env["ir.config_parameter"].set_param(
            self.setting_name,
            False,
        )
        self.sale_order._compute_payment_term_id()
        self.assertEqual(
            self.sale_order.payment_term_id,
            self.partner.property_payment_term_id,
            "Payment terms should be computed from partner_id when the option "
            "is not checked.",
        )

    def test_payment_terms_from_invoice_partner(self):
        """
        Test that payment terms are computed from partner_invoice_id
        when the option is checked.
        """
        self.env["ir.config_parameter"].set_param(
            self.setting_name,
            True,
        )
        self.sale_order._compute_payment_term_id()
        self.assertEqual(
            self.sale_order.payment_term_id,
            self.partner_invoice.property_payment_term_id,
            "Payment terms should be computed from partner_invoice_id when the "
            "option is checked.",
        )
