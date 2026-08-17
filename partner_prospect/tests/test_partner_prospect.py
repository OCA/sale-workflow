# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPartnerProspect(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.sale_order_model = cls.env["sale.order"]
        cls.partner_model = cls.env["res.partner"]
        cls.invoice_model = cls.env["account.move"]

        cls.partner1 = cls.partner_model.create({"name": "Partner1"})
        cls.partner2 = cls.partner_model.create(
            {
                "name": "Partner2",
                "parent_id": cls.partner1.id,
            }
        )
        cls.partner3 = cls.partner_model.create(
            {
                "name": "Partner3",
                "parent_id": cls.partner1.id,
            }
        )
        cls.partner4 = cls.partner_model.create({"name": "Partner4"})

        cls.product = cls.env.ref("product.product_product_4")

        cls.sale_order1 = cls.sale_order_model.create(
            {
                "partner_id": cls.partner1.id,
                "order_line": [
                    (0, 0, {"product_id": cls.product.id}),
                ],
            }
        )
        cls.sale_order2 = cls.sale_order_model.create(
            {
                "partner_id": cls.partner2.id,
                "order_line": [
                    (0, 0, {"product_id": cls.product.id}),
                ],
            }
        )
        cls.sale_order3 = cls.sale_order_model.create(
            {
                "partner_id": cls.partner4.id,
                "order_line": [
                    (0, 0, {"product_id": cls.product.id}),
                ],
            }
        )

    def test_partner_child_check(self):
        self.sale_order2.action_confirm()
        self.assertFalse(self.partner1.prospect, "Partner1 is a prospect")
        self.assertFalse(self.partner2.prospect, "Partner2 is a prospect")
        self.assertFalse(self.partner3.prospect, "Partner3 is a prospect")

    def test_partner_parent_check(self):
        self.sale_order1.action_confirm()
        self.assertFalse(self.partner1.prospect, "Partner1 is a prospect")
        self.assertFalse(self.partner2.prospect, "Partner2 is a prospect")
        self.assertFalse(self.partner3.prospect, "Partner3 is a prospect")

    def test_partner_prospect(self):
        self.assertTrue(self.partner4.prospect, "Partner4 is not a prospect")
        self.sale_order3.action_confirm()
        self.assertFalse(self.partner4.prospect, "Partner4 is a prospect")
        self.sale_order3._action_cancel()
        self.assertTrue(self.partner4.prospect, "Partner4 is not a prospect")

    def test_partner_child_check_invoice(self):
        ttype = "out_invoice"
        self.invoice_model.create(
            {
                "partner_id": self.partner2.id,
                "move_type": ttype,
            }
        )._onchange_partner_id()
        self.assertFalse(self.partner1.prospect, "Partner1 is a prospect")
        self.assertFalse(self.partner2.prospect, "Partner2 is a prospect")
        self.assertFalse(self.partner3.prospect, "Partner3 is a prospect")

    def test_partner_parent_check_invoice(self):
        ttype = "out_refund"
        self.invoice_model.create(
            {
                "partner_id": self.partner1.id,
                "move_type": ttype,
            }
        )._onchange_partner_id()
        self.assertFalse(self.partner1.prospect, "Partner1 is a prospect")
        self.assertFalse(self.partner2.prospect, "Partner2 is a prospect")
        self.assertFalse(self.partner3.prospect, "Partner3 is a prospect")
