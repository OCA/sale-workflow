# Copyright 2020 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase, Form


class TestPortalSaleMailLink(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestPortalSaleMailLink, cls).setUpClass()
        cls.template = cls.env.ref("sale.email_template_edi_sale")
        cls.preview = cls.env["email_template.preview"].with_context(
            template_id=cls.template.id)
        cls.partner = cls.env["res.partner"].create({
            "name": "Test Odoo",
        })
        cls.product = cls.env["product.product"].create({
            "name": "Test product",
            "type": "consu",
        })
        cls.company = cls.env.user.company_id

    def _new_sale_order(self):
        sale = self.env["sale.order"].create({
            "partner_id": self.partner.id,
        })
        sale.order_line.create({
            "order_id": sale.id,
            "product_id": self.product.id,
        })
        return sale

    def _test_preview_form(self, button_text, sale):
        self_ctx = self.preview.with_context(default_res_id=sale.id)
        with Form(self_ctx) as preview_form:
            self.assertTrue(button_text in preview_form.body_html)

    def test_edi_sale_template(self):
        """Test different default options"""
        # No portal options set
        self.company.portal_confirmation_sign = False
        self.company.portal_confirmation_pay = False
        sale_1 = self._new_sale_order()
        button_text = ">View {}".format(sale_1.name)
        self._test_preview_form(button_text, sale_1)
        # Ask order portal signature by default
        self.company.portal_confirmation_sign = True
        sale_2 = self._new_sale_order()
        button_text = ">Sign {}".format(sale_2.name)
        self._test_preview_form(button_text, sale_2)
        # Ask order portal payment by default
        self.company.portal_confirmation_pay = True
        sale_3 = self._new_sale_order()
        button_text = ">Pay {}".format(sale_3.name)
        self._test_preview_form(button_text, sale_3)
