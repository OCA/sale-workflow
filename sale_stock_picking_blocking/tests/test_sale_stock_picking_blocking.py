# Copyright 2024 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import users
from odoo.tests.form import Form

from .common import TestSaleDeliveryBlockSetup


class TestSaleDeliveryBlock(TestSaleDeliveryBlockSetup):
    @users("login@test-user.com")
    def test_check_auto_done(self):
        """Check an error is raised when blocking a sale order with auto-done enabled"""
        # Activate auto-done (in sudo mode: test user doesn't have access)
        config = self.env["res.config.settings"].sudo()
        config.create({"group_auto_done_setting": True}).execute()
        # Check settings constraints
        with self.assertRaises(ValidationError):
            self.sale_orders.write({"delivery_block_id": self.block_reasons[0].id})

    @users("login@test-user.com")
    def test_no_block(self):
        """Checks the picking creation workflow when SO has no block at confirmation"""
        so = self.sale_orders[0]
        so.delivery_block_id = self.env["sale.delivery.block.reason"]
        so.action_confirm()
        self.assertTrue(so.picking_ids, "A delivery should have been created")

    @users("login@test-user.com")
    def test_sale_stock_picking_blocking(self):
        """Checks the picking creation workflow when SO has a block at confirmation"""
        so = self.sale_orders[0]
        # Add a block, confirm, check no picking is created
        so.write({"delivery_block_id": self.block_reasons[0].id})
        so.action_confirm()
        self.assertFalse(so.picking_ids, "The delivery should have been blocked")
        # Remove block, check a picking is created automatically
        so.action_remove_delivery_block()
        self.assertTrue(so.picking_ids, "A delivery should have been made")

    @users("login@test-user.com")
    def test_default_delivery_block_partner(self):
        """Checks block is set from SO's partner"""
        with Form(self.env["sale.order"]) as so_form:
            so_form.partner_id = self.partners[1]  # Linked to block 2
            so_form.payment_term_id = self.payment_terms[2]  # Linked to block 3
        self.assertEqual(so_form.record.delivery_block_id, self.block_reasons[1])

    @users("login@test-user.com")
    def test_default_delivery_block_payment_term(self):
        """Checks block is set from SO's payment terms if SO's partner has no block"""
        with Form(self.env["sale.order"]) as so_form:
            so_form.partner_id = self.partners[0]  # Has no block
            so_form.payment_term_id = self.payment_terms[1]  # Linked to block 2
        self.assertEqual(so_form.record.delivery_block_id, self.block_reasons[1])

    @users("login@test-user.com")
    def test_sale_form_view_manual_delivery_block_not_overridden(self):
        """Checks the compute method does not override manual values set via UI"""
        # Test SO creation:
        # - partner linked to block 2
        # - payment term linked to block 3
        # - we add block 1 to the SO
        # => block 1 is kept
        with Form(self.env["sale.order"]) as sale_form_view:
            sale_form_view.partner_id = self.partners[1]  # Linked to block 2
            sale_form_view.payment_term_id = self.payment_terms[2]  # Linked to block 3
            sale_form_view.delivery_block_id = self.block_reasons[0]  # Block 1
        sale = sale_form_view.record
        self.assertEqual(sale.delivery_block_id, self.block_reasons[0])
        # Test SO update:
        # - partner linked to block 3
        # - payment term linked to block 2
        # - we remove the block from the SO
        # => SO block is kept empty
        with Form(self.env["sale.order"]) as sale_form_view:
            sale_form_view.partner_id = self.partners[2]  # Linked to block 3
            sale_form_view.payment_term_id = self.payment_terms[1]  # Linked to block 2
            sale_form_view.delivery_block_id = self.env["sale.delivery.block.reason"]
        sale = sale_form_view.record
        self.assertFalse(sale.delivery_block_id)

    def test_commercial_fields(self):
        """Checks ``default_delivery_block`` is managed by commercial entities"""
        self.assertIn(
            "default_delivery_block",
            self.env["res.partner"]._commercial_fields(),
            "default_delivery_block must be included in _commercial_fields().",
        )
