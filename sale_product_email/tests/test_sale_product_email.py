# Copyright 2020 Commown SCIC SAS (https://commown.fr)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestSaleProductEmail(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestSaleProductEmail, cls).setUpClass()
        cls.product_25 = cls.env.ref("product.product_product_25")
        cls.product_25.product_tmpl_id.write({
            'sale_confirmation_mail_template_id': cls.env.ref(
                'sale.email_template_edi_sale').id})
        cls.sale_order_1 = cls.env.ref("sale.sale_order_1")

    def test_send_sold_products_mail(self):
        self.sale_order_1.action_confirm()
        emails = self.env['mail.mail'].search([
            ('recipient_ids', 'in', [self.sale_order_1.partner_id.id]),
            ('model', '=', 'sale.order'),
            ('res_id', '=', self.sale_order_1.id)
        ])
        self.assertNotEqual(emails, False)
