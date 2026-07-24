# Copyright 2026 ForgeFlow, S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from .test_sale_order_approval_block import TestSaleOrderApprovalBlock


class TestSoApprovalBlockReason(TestSaleOrderApprovalBlock):
    def test_so_approval_block_manual_release(self):
        sale = self._create_sale(
            [(self.product1, 1), (self.product2, 5), (self.product3, 8)]
        )

        sale.approval_block_id = self.so_approval_block_reason.id
        self.assertTrue(sale.approval_blocked)

        sale.with_user(self.user2_id).button_release_approval_block()
        self.assertFalse(sale.approval_block_id)

        sale.with_user(self.user1_id).action_confirm()
        self.assertEqual(sale.state, "sale")

    def test_so_approval_block_release_via_wizard(self):
        sale = self._create_sale(
            [(self.product1, 1), (self.product2, 5), (self.product3, 8)]
        )

        sale.approval_block_id = self.so_approval_block_reason.id
        sale.with_user(self.user2_id).action_confirm()
        self.assertEqual(sale.state, "draft")

        wizard = (
            self.env["sale.exception.confirm"]
            .with_context(
                active_id=sale.id,
                active_ids=[sale.id],
                active_model=sale._name,
            )
            .create({"ignore": True})
        )
        wizard.action_confirm()

        self.assertEqual(sale.state, "sale")
