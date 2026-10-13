from lxml import html

from odoo.tests import TransactionCase


class TestSaleOrderIntroductionText(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.write(
            {"sale_order_introduction_text": "Test sale order introduction text"}
        )
        cls.partner = cls.env.ref("base.res_partner_1")

    def test_introduction_text(self):
        """Check sale order introduction text value at sale order level."""
        self.sale_order = self.env["sale.order"].create({"partner_id": self.partner.id})
        self.assertTrue(
            self.sale_order.sale_order_introduction_text,
            "Introduction text is not set",
        )
        self.assertEqual(
            html.fromstring(
                str(self.sale_order.sale_order_introduction_text)
            ).text_content(),
            "Test sale order introduction text",
            "Introduction text content is incorrect",
        )
