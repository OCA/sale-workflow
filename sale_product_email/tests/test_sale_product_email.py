# Copyright 2022-today Commown SCIC (https://commown.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSaleProductEmail(TransactionCase):

    test_email_subject = "Test product email template"

    @classmethod
    def setUpClass(cls):
        super(TestSaleProductEmail, cls).setUpClass()
        cls.product_25 = cls.env.ref("product.product_product_25")
        mail_template = cls.env.ref("sale.email_template_edi_sale").copy(
            {
                "subject": cls.test_email_subject,
            }
        )
        cls.product_25.product_tmpl_id.write(
            {"sale_confirmation_mail_template_id": mail_template.id}
        )
        cls.sale_order_1 = cls.env.ref("sale.sale_order_1")

    def _product_messages(self):
        return self.sale_order_1.message_ids.filtered(
            lambda m: m.subject == self.test_email_subject
        )

    def test_send_sold_products_mail(self):
        self.assertFalse(self._product_messages())
        self.sale_order_1.action_confirm()
        messages = self._product_messages()
        self.assertEqual(len(messages), 1)
        self.assertIn(self.sale_order_1.partner_id, messages.partner_ids)
