# Copyright 2013 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# Copyright 2018 Dreambits Technologies Pvt. Ltd. (<http://dreambits.in>)
# Copyright 2023 Simone Rubino - TAKOBI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests import common
from odoo.tools.safe_eval import safe_eval


class TestSaleOrderRevision(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestSaleOrderRevision, cls).setUpClass()
        cls.sale_order_model = cls.env['sale.order']
        cls.partner_id = cls.env.ref('base.res_partner_2').id
        cls.product_id1 = cls.env.ref('product.product_product_1').id

    def _create_sale_order(self):
        # Creating a sale order
        new_sale = self.sale_order_model.create({
            'partner_id': self.partner_id,
            'order_line': [(0, 0, {
                'product_id': self.product_id1,
                'product_uom_qty': '15.0'
            })]
        })
        return new_sale

    @staticmethod
    def _revision_sale_order(sale_order):
        # Cancel the sale order
        sale_order.action_cancel()
        # Create a new revision
        return sale_order.create_revision()

    def test_order_revision(self):
        """Check revision process"""
        # Create a Sale Order
        sale_order_1 = self._create_sale_order()

        # Create a revision of the Sale Order
        self._revision_sale_order(sale_order_1)

        # Check the previous revision of the sale order
        revision_1 = sale_order_1.current_revision_id
        self.assertEqual(sale_order_1.state, 'cancel')
        self.assertFalse(sale_order_1.active)

        # Check the current revision of the sale order
        self.assertEqual(revision_1.unrevisioned_name, sale_order_1.name)
        self.assertEqual(revision_1.state, 'draft')
        self.assertTrue(revision_1.active)
        self.assertEqual(revision_1.old_revision_ids, sale_order_1)
        self.assertEqual(revision_1.revision_number, 1)
        self.assertEqual(revision_1.name.endswith('-01'), True)
        self.assertEqual(revision_1.has_old_revisions, True)

        # Create a new revision of the Sale Order
        self._revision_sale_order(revision_1)
        revision_2 = revision_1.current_revision_id

        # Check the previous revision of the sale order
        self.assertEqual(revision_1.state, 'cancel')
        self.assertFalse(revision_1.active)

        # Check the current revision of the sale order
        self.assertEqual(revision_2.unrevisioned_name, sale_order_1.name)
        self.assertEqual(revision_2, sale_order_1.current_revision_id)
        self.assertEqual(revision_2.state, 'draft')
        self.assertTrue(revision_2.active)
        self.assertEqual(
            revision_2.old_revision_ids, sale_order_1 + revision_1)
        self.assertEqual(revision_2.revision_number, 2)
        self.assertEqual(revision_2.name.endswith('-02'), True)
        self.assertEqual(revision_2.has_old_revisions, True)

    def test_simple_copy(self):
        """Check copy process"""
        # Create a Sale Order
        sale_order_2 = self._create_sale_order()
        # Check the 'Order Reference' of the Sale Order
        self.assertEqual(sale_order_2.name, sale_order_2.unrevisioned_name)

        # Copy the Sale Order
        sale_order_3 = sale_order_2.copy()
        # Check the 'Order Reference' of the copied Sale Order
        self.assertEqual(sale_order_3.name, sale_order_3.unrevisioned_name)

    def _create_new_revision(self, sale_order):
        """Create and return a new Revision of `sale_order`."""
        action = self._revision_sale_order(sale_order)
        model_name = action["res_model"]
        domain = safe_eval(action["domain"])
        revision = self.env[model_name].search(domain)
        return revision

    def _check_order_confirmation_failure(self, order):
        """Confirming `sale_order` fails because it has a new Revision."""
        # Arrange
        order.action_draft()
        # pre-condition
        revision = order.current_revision_id
        self.assertTrue(revision)

        # Act
        with self.assertRaises(UserError) as ue, self.env.cr.savepoint():
            order.action_confirm()

        # Assert
        exc_message = ue.exception.args[0]
        self.assertIn(order.display_name, exc_message)
        self.assertIn(revision.display_name, exc_message)
        self.assertNotEqual(order.state, "sale")

    def test_confirm_old_revision(self):
        """Only the latest Revision can be confirmed."""
        # Arrange
        sale_order = self._create_sale_order()
        revision_1 = self._create_new_revision(sale_order)
        revision_2 = self._create_new_revision(revision_1)
        # pre-condition
        self.assertEqual(sale_order.current_revision_id, revision_2)
        self.assertEqual(revision_1.current_revision_id, revision_2)

        # Act
        self._check_order_confirmation_failure(sale_order)
        self._check_order_confirmation_failure(revision_1)
        revision_2.action_confirm()

        # Assert
        self.assertEqual(revision_2.state, "sale")
