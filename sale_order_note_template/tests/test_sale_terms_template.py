# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestSaleTermsTemplate(TransactionCase):
    def setUp(self):
        super().setUp()
        self.term_template = self.env["sale.terms_template"].create(
            {
                "name": "My terms and conditions template",
                "text": "<p>Terms template ${object.partner_id.name}</p>",
            }
        )
        self.sale_order = self.env.ref("sale.sale_order_2")

    def test_get_value(self):
        self.assertEqual(
            self.term_template.get_value(self.sale_order),
            "<p>Terms template Ready Mat</p>",
        )

    def test_get_value_with_translation(self):
        self.env["res.lang"]._activate_lang("fr_BE")
        self.sale_order.partner_id.lang = "fr_BE"
        self.term_template.with_context(lang="fr_BE").write(
            {"text": "<p>Testing translated fr_BE `${object.partner_id.name}`</p>"}
        )
        self.assertEqual(
            self.term_template.get_value(self.sale_order),
            "<p>Testing translated fr_BE `Ready Mat`</p>",
        )
