# Copyright 2025 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSaleOrderDeliveryWizard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.pricelist_exc = cls.env["product.pricelist"].create(
            {"name": "Test Pricelist Tax Excluded"}
        )
        cls.pricelist_inc = cls.env["product.pricelist"].create(
            {
                "name": "Test Pricelist Tax Included",
                "price_include_taxes": True,
            }
        )

    def _action_context(self, pricelist):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": pricelist.id,
            }
        )
        return order.action_open_delivery_wizard()["context"]

    def test_action_open_delivery_wizard_price_include_taxes_false(self):
        self.assertFalse(
            self._action_context(self.pricelist_exc)["price_include_taxes"]
        )

    def test_action_open_delivery_wizard_price_include_taxes_true(self):
        self.assertTrue(self._action_context(self.pricelist_inc)["price_include_taxes"])
