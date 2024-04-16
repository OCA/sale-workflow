# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestWarnOptions(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        cls.partner_sale_warn_warning = cls.env["warn.option"].create(
            {
                "name": "warning",
                "allowed_warning_usage": "partner_sale_warn",
                "allowed_warning_type": "warning",
            }
        )
        cls.partner_sale_warn_blocking = cls.env["warn.option"].create(
            {
                "name": "block",
                "allowed_warning_usage": "partner_sale_warn",
                "allowed_warning_type": "block",
            }
        )
        cls.product = cls.env["product.template"].create(
            {
                "name": "Test Product",
            }
        )
        cls.product_sale_line_warn_warning = cls.env["warn.option"].create(
            {
                "name": "warning",
                "allowed_warning_usage": "product_sale_warn",
                "allowed_warning_type": "warning",
            }
        )
        cls.product_sale_line_warn_blocking = cls.env["warn.option"].create(
            {
                "name": "block",
                "allowed_warning_usage": "product_sale_warn",
                "allowed_warning_type": "block",
            }
        )

    def test_partner_warn_options(self):
        """Test Warn Options on Partner Form"""
        with Form(self.partner) as partner_f:
            partner_f.sale_warn = "warning"
            partner_f.sale_warn_option = self.partner_sale_warn_warning
            self.assertEqual(partner_f.sale_warn_msg, "warning")
            partner_f.sale_warn = "block"
            partner_f.sale_warn_option = self.partner_sale_warn_blocking
            self.assertEqual(partner_f.sale_warn_msg, "block")

    def test_product_warn_options(self):
        """Test Warn Options on Product Form"""
        with Form(self.product) as product_f:
            product_f.sale_line_warn = "warning"
            product_f.sale_line_warn_option = self.product_sale_line_warn_warning
            self.assertEqual(product_f.sale_line_warn_msg, "warning")
            product_f.sale_line_warn = "block"
            product_f.sale_line_warn_option = self.product_sale_line_warn_blocking
            self.assertEqual(product_f.sale_line_warn_msg, "block")
