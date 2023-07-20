# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.base_revision.tests import test_base_revision


class TestSaleOrderRevision(test_base_revision.TestBaseRevision):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.revision_model = cls.env["sale.order"]
        cls.partner = cls.env["res.partner"].create({"name": "Mr Odoo"})
        cls.product = cls.env["product.product"].create({"name": "Test product"})

    def _create_tester(self, vals_list=None):
        if not vals_list:
            vals_list = [{}]
        for vals in vals_list:
            if "partner_id" not in vals:
                vals["partner_id"] = self.partner.id
            if "order_line" not in vals:
                vals["order_line"] = [(0, 0, {"product_id": self.product.id})]
        return super()._create_tester(vals_list)

    @staticmethod
    def _revision_sale_order(sale_order):
        # Cancel the tester
        sale_order.action_cancel()
        # Create a new revision
        return sale_order.create_revision()

    def test_order_revision(self):
        sale_order_1 = self._create_tester()

        # Create a revision of the Sale Order
        self._revision_sale_order(sale_order_1)

        # Check the previous revision of the sale order
        revision_1 = sale_order_1.current_revision_id
        self.assertEqual(sale_order_1.state, "cancel")

        # Check the current revision of the sale order
        self.assertEqual(revision_1.unrevisioned_name, sale_order_1.name)
        self.assertEqual(revision_1.state, "draft")
        self.assertTrue(revision_1.active)
        self.assertEqual(revision_1.old_revision_ids, sale_order_1)
        self.assertEqual(revision_1.revision_number, 1)
        self.assertEqual(revision_1.name.endswith("-01"), True)
        self.assertEqual(revision_1.has_old_revisions, True)

        # Create a new revision of the Sale Order
        self._revision_sale_order(revision_1)
        revision_2 = revision_1.current_revision_id

        # Check the previous revision of the sale order
        self.assertEqual(revision_1.state, "cancel")
        self.assertFalse(revision_1.active)

        # Check the current revision of the sale order
        self.assertEqual(revision_2.unrevisioned_name, sale_order_1.name)
        self.assertEqual(revision_2, sale_order_1.current_revision_id)
        self.assertEqual(revision_2.state, "draft")
        self.assertTrue(revision_2.active)
        self.assertEqual(revision_2.old_revision_ids, sale_order_1 + revision_1)
        self.assertEqual(revision_2.revision_number, 2)
        self.assertEqual(revision_2.name.endswith("-02"), True)
        self.assertEqual(revision_2.has_old_revisions, True)
