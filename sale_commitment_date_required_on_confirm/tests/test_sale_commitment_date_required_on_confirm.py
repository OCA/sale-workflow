# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import fields
from odoo.exceptions import UserError

from odoo.addons.base.tests.common import BaseCommon


class TestSaleCommitmentDateRequiredOnConfirm(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company.sale_commitment_date_required = True
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.product = cls.env["product.product"].create({"name": "Test Product"})
        cls.order = cls.env["sale.order"].create({"partner_id": cls.partner.id})

    def _add_line(self):
        return self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "price_unit": 100,
            }
        )

    def test_quotation_without_commitment_date_is_editable(self):
        """The delivery date is not required to write on the quotation nor to
        add order lines to it.
        """
        self.order.client_order_ref = "REF-1"
        line = self._add_line()
        self.assertFalse(self.order.commitment_date)
        self.assertEqual(self.order.state, "draft")
        self.assertIn(line, self.order.order_line)

    def test_confirm_without_commitment_date_is_refused(self):
        self._add_line()
        with self.assertRaises(UserError):
            self.order.action_confirm()
        self.assertEqual(self.order.state, "draft")

    def test_confirm_with_commitment_date(self):
        self._add_line()
        self.order.commitment_date = fields.Datetime.now()
        self.order.action_confirm()
        self.assertEqual(self.order.state, "sale")

    def test_confirm_without_commitment_date_when_not_required(self):
        self.company.sale_commitment_date_required = False
        self._add_line()
        self.order.action_confirm()
        self.assertEqual(self.order.state, "sale")

    def test_confirmation_error_message_of_the_core_has_precedence(self):
        """An order that the core already refuses to confirm keeps its own
        error message.
        """
        self.order.action_cancel()
        self.assertFalse(self.order.commitment_date)
        self.assertNotEqual(
            self.order._confirmation_error_message(),
            "You cannot confirm this order without a delivery date.",
        )
