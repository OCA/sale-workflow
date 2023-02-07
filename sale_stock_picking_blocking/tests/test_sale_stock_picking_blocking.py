# Copyright 2019 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import ValidationError
from odoo.tests import Form, common


class TestSaleDeliveryBlock(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.so_model = cls.env["sale.order"]
        cls.sol_model = cls.env["sale.order.line"]
        cls.usr_model = cls.env["res.users"]
        cls.block_model = cls.env["sale.delivery.block.reason"]
        group_ids = [
            cls.env.ref("sale_stock_picking_blocking.group_sale_delivery_block").id,
            cls.env.ref("sales_team.group_sale_manager").id,
        ]
        user_dict = {
            "name": "User test",
            "login": "tua@example.com",
            "password": "base-test-passwd",
            "email": "armande.hruser@example.com",
            "groups_id": [(6, 0, group_ids)],
        }
        cls.user_test = cls.usr_model.create(user_dict)
        # Create product:
        prod_dict = {
            "name": "test product",
            "type": "product",
        }
        product = cls.env["product.product"].with_user(cls.user_test).create(prod_dict)
        # Create Sale order:
        # TODO/TMP:
        # - we explicitely add a name to avoid
        #   a weird issue occuring randomly during tests
        # - seems related to sale_order_revision,
        #   further investigations ongoing
        so_dict = {
            "partner_id": cls.env.ref("base.res_partner_1").id,
            "name": "Test Sale Delivery Block",
        }
        cls.sale_order = cls.so_model.with_user(cls.user_test).create(so_dict)
        # Create Sale order lines:
        sol_dict = {
            "order_id": cls.sale_order.id,
            "product_id": product.id,
            "product_uom_qty": 1.0,
        }
        cls.sale_order_line = cls.sol_model.with_user(cls.user_test).create(sol_dict)

    def test_check_auto_done(self):
        # Set active auto done configuration
        config = self.env["res.config.settings"].create(
            {"group_auto_done_setting": True}
        )
        config.execute()
        block_reason = self.block_model.with_user(self.user_test).create(
            {"name": "Test Block."}
        )
        so = self.sale_order
        # Check settings constraints
        with self.assertRaises(ValidationError):
            so.write({"delivery_block_id": block_reason.id})

    def _picking_comp(self, so):
        """count created pickings"""
        count = len(so.picking_ids)
        return count

    def test_no_block(self):
        """Tests if normal behaviour without block."""
        so = self.sale_order
        so.action_confirm()
        pick = self._picking_comp(so)
        self.assertNotEqual(pick, 0, "A delivery should have been made")

    def test_sale_stock_picking_blocking(self):
        # Create Sales order block reason:
        block_reason = self.block_model.with_user(self.user_test).create(
            {"name": "Test Block."}
        )
        so = self.sale_order
        so.write({"delivery_block_id": block_reason.id})
        so.action_confirm()
        self._picking_comp(so)
        pick = self._picking_comp(so)
        self.assertEqual(pick, 0, "The delivery should have been blocked")
        # Remove block
        so.action_remove_delivery_block()
        pick = self._picking_comp(so)
        self.assertNotEqual(pick, 0, "A delivery should have been made")

    def test_default_delivery_block(self):
        block_reason = self.block_model.with_user(self.user_test).create(
            {"name": "Test Block."}
        )
        partner_block = self.env["res.partner"].create(
            {
                "name": "Foo",
                "default_delivery_block": block_reason.id,
            }
        )
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = partner_block
        so = so_form.save()
        self.assertEqual(so.delivery_block_id, block_reason)
        self.assertEqual(so.copy().delivery_block_id, block_reason)
