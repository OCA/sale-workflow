# Copyright 2024 Ecosoft Co., Ltd. (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo.tests.common import Form, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSaleOrderSequenceOption(TransactionCase):
    def setUp(self):
        super(TestSaleOrderSequenceOption, self).setUp()
        self.partner_1 = self.env.ref("base.res_partner_1")
        self.partner_2 = self.env.ref("base.res_partner_address_1")
        self.sale_seq_option = self.env.ref(
            "sale_order_sequence_option.sale_sequence_option"
        )

    def _create_quotation(self, partner):
        sale_form = Form(self.env["sale.order"])
        sale_form.partner_id = partner
        quotation = sale_form.save()
        return quotation

    def test_sale_sequence_options(self):
        """Test different kind of sequences"""
        self.sale_seq_option.use_sequence_option = True
        # Company
        self.quotation1 = self._create_quotation(self.partner_1)
        self.assertIn("SOC", self.quotation1.name)
        old_name = self.quotation1.name
        self.quotation1.action_confirm()
        self.assertEqual(old_name, self.quotation1.name)
        # Individual
        self.quotation2 = self._create_quotation(self.partner_2)
        self.assertIn("SOI", self.quotation2.name)
        old_name = self.quotation2.name
        self.quotation2.action_confirm()
        self.assertEqual(old_name, self.quotation2.name)
        self.quotation2.action_cancel()
        self.quotation2.action_draft()
        self.quotation2.action_confirm()
        self.assertEqual(old_name, self.quotation2.name)
