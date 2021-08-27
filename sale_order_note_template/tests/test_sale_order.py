# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestSaleOrder(TransactionCase):
    def setUp(self):
        super().setUp()
        self.term_template = self.env["sale.terms_template"].create(
            {
                "name": "My terms and conditions template",
                "text": "<p>Terms template ${object.partner_id.name}</p>",
            }
        )
        self.sale_order = self.env.ref("sale.sale_order_2")

    def test_on_change_term_template(self):
        self.assertEqual(self.sale_order.note, "")
        self.sale_order.terms_template_id = self.term_template
        self.sale_order._onchange_terms_template_id()
        self.assertEqual(self.sale_order.note, "<p>Terms template Ready Mat</p>")
