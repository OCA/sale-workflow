# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.base.tests.common import BaseCommon


class TestSaleOrder(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.term_template = cls.env["sale.terms_template"].create(
            {
                "name": "My terms and conditions template",
                "text": "<p>Terms template {{ object.partner_id.name }}</p>",
            }
        )
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
            }
        )

    def test_on_change_term_template(self):
        self.assertFalse(self.sale_order.note)
        self.sale_order.terms_template_id = self.term_template
        self.sale_order._onchange_terms_template_id()
        self.assertEqual(
            self.sale_order.note, f"<p>Terms template {self.partner.name}</p>"
        )
