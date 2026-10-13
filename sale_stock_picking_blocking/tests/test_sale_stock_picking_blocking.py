# Copyright 2019 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# Copyright 2026 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests import Form, common


class TestSaleDeliveryBlock(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.so_model = cls.env["sale.order"]
        cls.sol_model = cls.env["sale.order.line"]
        cls.usr_model = cls.env["res.users"]
        cls.block_model = cls.env["sale.delivery.block.reason"]
        cls.partner_model = cls.env["res.partner"]
        cls.payment_term_model = cls.env["account.payment.term"]
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

        cls.block_reason_1 = cls.block_model.with_user(cls.user_test).create(
            {"name": "Test Block 1"}
        )
        cls.block_reason_2 = cls.block_model.with_user(cls.user_test).create(
            {"name": "Test Block 2"}
        )

        cls.payment_term_no_block = cls.payment_term_model.create(
            {"name": "Test Payment Term No Block"}
        )
        cls.payment_term_with_block = cls.payment_term_model.create(
            {
                "name": "Test Payment Term With Block",
                "default_delivery_block_reason_id": cls.block_reason_2.id,
            }
        )

        cls.partner_no_block = cls.partner_model.create(
            {
                "name": "Test Partner No Block",
                "property_payment_term_id": cls.payment_term_no_block.id,
            }
        )
        cls.partner_with_block = cls.partner_model.create(
            {
                "name": "Test Partner With Block",
                "default_delivery_block": cls.block_reason_1.id,
                "property_payment_term_id": cls.payment_term_no_block.id,
            }
        )
        cls.partner_with_payment_term_block = cls.partner_model.create(
            {
                "name": "Test Partner With Payment Term Block",
                "property_payment_term_id": cls.payment_term_with_block.id,
            }
        )
        cls.partner_with_both_blocks = cls.partner_model.create(
            {
                "name": "Test Partner With Both Blocks",
                "default_delivery_block": cls.block_reason_1.id,
                "property_payment_term_id": cls.payment_term_with_block.id,
            }
        )

    def test_block_with_auto_done_enabled(self):
        # Set active auto done configuration
        config = self.env["res.config.settings"].create(
            {"group_auto_done_setting": True}
        )
        config.execute()
        block_reason = self.block_model.with_user(self.user_test).create(
            {"name": "Test Block."}
        )
        so = self.sale_order
        so.write({"delivery_block_id": block_reason.id})
        so.action_confirm()
        self.assertEqual(so.state, "sale")
        self._picking_comp(so)
        pick = self._picking_comp(so)
        self.assertEqual(pick, 0, "The delivery should have been blocked")
        # Remove block
        so.action_remove_delivery_block()
        pick = self._picking_comp(so)
        self.assertNotEqual(pick, 0, "A delivery should have been made")
        self.assertEqual(so.state, "done")

    def test_no_block_with_auto_done_enabled(self):
        """Tests if normal behaviour without block."""
        config = self.env["res.config.settings"].create(
            {"group_auto_done_setting": True}
        )
        config.execute()
        so = self.sale_order
        so.action_confirm()
        pick = self._picking_comp(so)
        self.assertNotEqual(pick, 0, "A delivery should have been made")
        self.assertEqual(so.state, "done")

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

    def test_default_delivery_block_partner(self):
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.partner_with_block
        so = so_form.save()
        self.assertEqual(so.delivery_block_id, self.block_reason_1)
        self.assertEqual(so.copy().delivery_block_id, self.block_reason_1)

    def test_default_delivery_block_payment_term(self):
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.partner_no_block
        so_form.payment_term_id = self.payment_term_with_block
        so = so_form.save()
        self.assertEqual(so.delivery_block_id, self.block_reason_2)
        self.assertEqual(so.copy().delivery_block_id, self.block_reason_2)

    def test_default_delivery_block_partner_has_priority_over_payment_term(self):
        so = self.so_model.create(
            {
                "partner_id": self.partner_with_both_blocks.id,
                "payment_term_id": self.payment_term_with_block.id,
                "name": "Test SO Partner Priority",
            }
        )
        self.assertEqual(so.delivery_block_id, self.block_reason_1)

    def test_manual_delivery_block_is_preserved_on_create(self):
        so = self.so_model.create(
            {
                "partner_id": self.partner_no_block.id,
                "payment_term_id": self.payment_term_no_block.id,
                "delivery_block_id": self.block_reason_2.id,
                "name": "Test SO Manual Create",
            }
        )
        self.assertEqual(so.delivery_block_id, self.block_reason_2)

    def test_manual_delivery_block_overrides_partner_default_on_create(self):
        so = self.so_model.create(
            {
                "partner_id": self.partner_with_block.id,
                "payment_term_id": self.payment_term_no_block.id,
                "delivery_block_id": self.block_reason_2.id,
                "name": "Test SO Manual Over Partner Default",
            }
        )
        self.assertEqual(so.delivery_block_id, self.block_reason_2)

    def test_manual_delivery_block_overrides_payment_term_default_on_create(self):
        so = self.so_model.create(
            {
                "partner_id": self.partner_with_payment_term_block.id,
                "payment_term_id": self.payment_term_with_block.id,
                "delivery_block_id": self.block_reason_1.id,
                "name": "Test SO Manual Over Payment Term Default",
            }
        )
        self.assertEqual(so.delivery_block_id, self.block_reason_1)

    def test_write_unrelated_field_keeps_delivery_block(self):
        so = self.so_model.create(
            {
                "partner_id": self.partner_with_block.id,
                "payment_term_id": self.payment_term_no_block.id,
                "name": "Test SO Unrelated Write",
            }
        )
        self.assertEqual(so.delivery_block_id, self.block_reason_1)

        so.write({"client_order_ref": "REF123"})
        self.assertEqual(so.delivery_block_id, self.block_reason_1)

    def test_copy_keeps_payment_term_default_delivery_block(self):
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.partner_no_block
        so_form.payment_term_id = self.payment_term_with_block
        so = so_form.save()

        self.assertEqual(so.delivery_block_id, self.block_reason_2)
        self.assertEqual(so.copy().delivery_block_id, self.block_reason_2)

    def test_write_explicit_false_delivery_block_has_priority(self):
        so = self.so_model.create(
            {
                "partner_id": self.partner_with_block.id,
                "payment_term_id": self.payment_term_no_block.id,
                "name": "Test SO Explicit False Delivery Block",
            }
        )
        self.assertEqual(so.delivery_block_id, self.block_reason_1)

        so.write({"delivery_block_id": False})
        self.assertFalse(so.delivery_block_id)
