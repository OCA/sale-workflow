# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestSalePartnerOrderTemplate(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.order_template = cls.env["sale.order.template"].create(
            {"name": "Test Quotation Template"}
        )
        cls.other_order_template = cls.env["sale.order.template"].create(
            {"name": "Other Quotation Template"}
        )
        cls.partner.sale_order_template_id = cls.order_template
        cls.other_partner = cls.env["res.partner"].create(
            {
                "name": "Partner with another template",
                "sale_order_template_id": cls.other_order_template.id,
            }
        )
        cls.partner_without_template = cls.env["res.partner"].create(
            {"name": "Partner w/o template"}
        )

    def _create_order(self, partner, **values):
        return self.env["sale.order"].create({"partner_id": partner.id, **values})

    def test_order_template_from_partner(self):
        order = self._create_order(self.partner)
        self.assertEqual(order.sale_order_template_id, self.order_template)

    def test_no_order_template_on_partner(self):
        order = self._create_order(self.partner_without_template)
        self.assertFalse(order.sale_order_template_id)

    def test_order_template_updated_on_partner_change(self):
        order = self._create_order(self.partner)
        order.partner_id = self.other_partner
        self.assertEqual(order.sale_order_template_id, self.other_order_template)

    def test_order_template_kept_when_new_partner_has_none(self):
        order = self._create_order(self.partner)
        order.partner_id = self.partner_without_template
        self.assertEqual(order.sale_order_template_id, self.order_template)

    def test_order_template_explicitly_set(self):
        order = self._create_order(
            self.partner, sale_order_template_id=self.other_order_template.id
        )
        self.assertEqual(order.sale_order_template_id, self.other_order_template)
