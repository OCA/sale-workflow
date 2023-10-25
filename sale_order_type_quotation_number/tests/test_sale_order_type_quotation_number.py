# Copyright 2023 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import odoo.tests.common as common
from odoo.tests import Form, tagged


@tagged("post_install", "-at_install")
class TestSaleOrderTypeQuotationNumber(common.TransactionCase):
    def setUp(self):
        super(TestSaleOrderTypeQuotationNumber, self).setUp()
        self.sale_seq = self.env["ir.sequence"].create(
            {"name": "Sale Seq. 1", "code": "sale.order", "prefix": "SO1", "padding": 5}
        )
        self.quotation_seq_1 = self.env["ir.sequence"].create(
            {
                "name": "Quotation Seq. 1",
                "code": "sale.quotation",
                "prefix": "Q1",
                "padding": 5,
            }
        )
        self.quotation_seq_2 = self.env["ir.sequence"].create(
            {
                "name": "Quotation Seq. 2",
                "code": "sale.quotation",
                "prefix": "Q2",
                "padding": 5,
            }
        )
        self.order_type_1 = self.env["sale.order.type"].create(
            {
                "name": "Test Sale Order Type 1",
                "sequence_id": self.sale_seq.id,
                "quotation_sequence_id": self.quotation_seq_1.id,
            }
        )
        self.order_type_2 = self.env["sale.order.type"].create(
            {
                "name": "Test Sale Order Type 2",
                "sequence_id": self.sale_seq.id,
                "quotation_sequence_id": self.quotation_seq_2.id,
            }
        )
        self.partner = self.env.ref("base.res_partner_1")
        self.env.company.write({"keep_name_so": False})

    def create_sale_order(self, partner=False):
        sale_form = Form(self.env["sale.order"])
        sale_form.partner_id = self.partner
        sale_form.type_id = self.order_type_1
        return sale_form.save()

    def test_quotation_seq(self):
        order = self.create_sale_order()
        self.assertEqual(order.name[:2], "Q1")
        self.assertFalse(order.recompute_quotation_seq)

    def test_quotation_seq_change(self):
        order = self.create_sale_order()
        self.assertEqual(order.name[:2], "Q1")
        order.type_id = self.order_type_2
        self.assertTrue(order.recompute_quotation_seq)
        order.action_recompute_quotation_seq()
        self.assertEqual(order.name[:2], "Q2")

    def test_order_type_seq(self):
        order = self.create_sale_order()
        order.action_confirm()
        self.assertEqual(order.name[:3], "SO1")
