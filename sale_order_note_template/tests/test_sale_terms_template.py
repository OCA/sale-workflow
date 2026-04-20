# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.base.tests.common import BaseCommon


class TestSaleTermsTemplate(BaseCommon):
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

    def test_get_value(self):
        self.assertEqual(
            self.term_template.get_value(self.sale_order),
            f"<p>Terms template {self.partner.name}</p>",
        )

    def test_get_value_with_translation(self):
        # Ensure 'fr_BE' is loaded
        self.env["res.lang"]._activate_lang("fr_BE")
        self.sale_order.partner_id.lang = "fr_BE"

        # We need to translate the 'text' field of the template
        self.term_template.with_context(lang="fr_BE").write(
            {"text": "<p>Testing translated fr_BE {{ object.partner_id.name }}</p>"}
        )

        # Verify rendered value for the order in fr_BE
        rendered = self.term_template.get_value(self.sale_order)
        self.assertEqual(
            rendered,
            f"<p>Testing translated fr_BE {self.partner.name}</p>",
        )
