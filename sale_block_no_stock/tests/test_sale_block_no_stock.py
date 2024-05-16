# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from freezegun import freeze_time

from odoo.fields import Command
from odoo.tests.common import TransactionCase, new_test_user, tagged


@freeze_time("2024-01-01")
@tagged("post_install", "-at_install")
class TestSaleBlockNoStock(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.user.company_id
        cls.saleblock_user = new_test_user(
            cls.env,
            "saleblock",
            "sales_team.group_sale_manager,stock.group_stock_manager,base.group_system",
            company_ids=[Command.set(cls.company.ids)],
        )

        cls.f_qty_today = cls.env.ref(
            "sale_stock.field_sale_order_line__qty_available_today"
        )
        cls.f_free = cls.env.ref("sale_stock.field_sale_order_line__free_qty_today")
        cls.f_virtual = cls.env.ref(
            "sale_stock.field_sale_order_line__virtual_available_at_date"
        )

        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )
        cls.product_packaging = cls.env["product.packaging"].create(
            {
                "name": "Half Unit",
                "product_id": cls.product.id,
                "qty": 0.5,
            }
        )
        cls.quant = cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "quantity": 1,
                "company_id": cls.company.id,
            }
        )
        cls.sale = cls.env["sale.order"].create(
            {
                "state": "draft",
                "company_id": cls.company.id,
                "partner_id": cls.partner.id,
                "commitment_date": "2024-01-01",
                "user_id": cls.saleblock_user.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                            "product_uom": cls.env.ref("uom.product_uom_dozen").id,
                        },
                    )
                ],
            }
        )
        cls.in_picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "company_id": cls.company.id,
                "location_id": cls.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": cls.env.ref("stock.stock_location_stock").id,
                "scheduled_date": "2024-01-05",
                "state": "assigned",
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Move",
                            "product_id": cls.product.id,
                            "product_uom_qty": 11.0,
                            "product_uom": cls.product.uom_id.id,
                            "location_id": cls.env.ref(
                                "stock.stock_location_suppliers"
                            ).id,
                            "location_dest_id": cls.env.ref(
                                "stock.stock_location_stock"
                            ).id,
                        },
                    )
                ],
            }
        )
        cls.in_picking.move_ids[0].quantity_done = 11.0

    def _get_wizard(self, wizard_user, wizard_action):
        """Returns a new wizard instance from the given action."""
        self.assertEqual(isinstance(wizard_action, dict), True)
        self.assertEqual(wizard_action["res_model"], "sale.order.block.wizard")
        wiz_vals = (
            self.env[wizard_action["res_model"]]
            .with_context(**wizard_action["context"])
            .default_get(["sale_line_block_ids"])
        )
        return (
            self.env[wizard_action["res_model"]]
            .with_user(wizard_user.id)
            .with_context(uid=wizard_user.id)
            .create(wiz_vals)
        )

    def test_sale_blocking_qty_available_today(self):
        """Test Sale Order Blocking with Quantity Available Today."""
        self.company.sale_line_block_allowed_groups = False
        self.company.sale_line_field_block = self.f_qty_today
        # Block: No 1 Dozen in stock
        wizard = self._get_wizard(
            self.saleblock_user,
            self.sale.with_user(self.saleblock_user.id).action_confirm(),
        )
        self.assertEqual(len(wizard.sale_line_block_ids), 1)
        # Block: No 2 Units in stock
        self.sale.order_line[0].product_uom_qty = 2
        self.sale.order_line[0].product_uom = self.env.ref("uom.product_uom_unit").id
        wizard = self._get_wizard(
            self.saleblock_user,
            self.sale.with_user(self.saleblock_user.id).action_confirm(),
        )
        self.assertEqual(len(wizard.sale_line_block_ids), 1)
        self.assertFalse(wizard.confirmation_allowed)

    def test_sale_blocking_free_qty_today(self):
        """Test Sale Order Blocking with Free Quantity Available Today."""
        self.company.sale_line_block_allowed_groups = False
        self.company.sale_line_field_block = self.f_free
        # Change quantities to 1 Unit
        self.sale.order_line[0].product_uom_qty = 1
        self.sale.order_line[0].product_uom = self.env.ref("uom.product_uom_unit").id
        # Confirm sale and create a new Sale to check reserved quantity
        self.sale.with_user(self.saleblock_user.id).action_confirm()
        self.assertNotEqual(self.sale.state, "draft")
        self.sale.picking_ids.action_confirm()
        new_sale = self.env["sale.order"].create(
            {
                "state": "draft",
                "company_id": self.company.id,
                "partner_id": self.partner.id,
                "commitment_date": "2024-01-01",
                "user_id": self.saleblock_user.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "product_uom": self.env.ref("uom.product_uom_dozen").id,
                        },
                    )
                ],
            }
        )
        # Block: No unreserved 1 Unit on 2024-01-01
        wizard = self._get_wizard(
            self.saleblock_user,
            new_sale.with_user(self.saleblock_user.id).action_confirm(),
        )
        self.assertEqual(len(wizard.sale_line_block_ids), 1)
        self.assertFalse(wizard.confirmation_allowed)

    def test_sale_blocking_virtual_available_at_date(self):
        """Test Sale Order Blocking with Virtual Available at Date (Forecast)."""
        self.company.sale_line_block_allowed_groups = False
        self.company.sale_line_field_block = self.f_virtual
        # Block: No 1 Dozen on 2024-01-01
        wizard = self._get_wizard(
            self.saleblock_user,
            self.sale.with_user(self.saleblock_user.id).action_confirm(),
        )
        self.assertEqual(len(wizard.sale_line_block_ids), 1)
        self.assertFalse(wizard.confirmation_allowed)
        self.sale.commitment_date = "2024-01-05"
        # No Block: 1 Dozen on 2024-01-05
        self.sale.with_user(self.saleblock_user.id).action_confirm()
        self.assertNotEqual(self.sale.state, "draft")

    def test_sale_blocking_allowed_groups(self):
        """Test Sale Order Blocking with Allowed Groups."""
        self.company.sale_line_block_allowed_groups = [
            (6, 0, self.env.ref("sales_team.group_sale_manager").ids)
        ]
        self.company.sale_line_field_block = self.f_qty_today
        # No Block: No 1 Dozen on 2024-01-01 + allowed groups
        wizard = self._get_wizard(
            self.saleblock_user,
            self.sale.with_user(self.saleblock_user.id).action_confirm(),
        )
        self.assertEqual(len(wizard.sale_line_block_ids), 1)
        self.assertTrue(wizard.confirmation_allowed)
        wizard.with_user(self.saleblock_user.id).confirm()
        self.assertNotEqual(self.sale.state, "draft")

    def test_sale_blocking_not_allowed_groups(self):
        """Test Sale Order Blocking with Not Allowed Groups."""
        self.company.sale_line_block_allowed_groups = False
        self.company.sale_line_field_block = self.f_qty_today
        # No Block: No 1 Dozen on 2024-01-01 + not allowed groups
        wizard = self._get_wizard(
            self.saleblock_user,
            self.sale.with_user(self.saleblock_user.id).action_confirm(),
        )
        self.assertEqual(len(wizard.sale_line_block_ids), 1)
        self.assertFalse(wizard.confirmation_allowed)

    def test_sale_adjust_uom_quantity(self):
        """Test Wizard Adjusting Quantity."""
        self.company.sale_line_block_allowed_groups = False
        self.company.sale_line_field_block = self.f_qty_today
        # Block: No 2 Units in stock
        self.sale.order_line[0].product_uom_qty = 2
        self.sale.order_line[0].product_uom = self.env.ref("uom.product_uom_unit").id
        wizard = self._get_wizard(
            self.saleblock_user,
            self.sale.with_user(self.saleblock_user.id).action_confirm(),
        )
        self.assertEqual(len(wizard.sale_line_block_ids), 1)
        # Wizard: Adjust Quantities to 1 Unit
        wizard.action_adjust_uom_quantity()
        self.assertEqual(self.sale.order_line[0].product_uom_qty, 1)
        # No Block: 1 Unit in stock
        self.sale.with_user(self.saleblock_user.id).action_confirm()
        self.assertNotEqual(self.sale.state, "draft")

    def test_sale_adjust_packaging_quantity(self):
        """Test Wizard Adjusting Packaging Quantity."""
        self.company.sale_line_block_allowed_groups = False
        self.company.sale_line_field_block = self.f_qty_today
        # Block: No 2 Units in stock (4 Packagings)
        self.sale.order_line[0].product_uom = self.env.ref("uom.product_uom_unit").id
        self.sale.order_line[0].product_uom_qty = 4 * self.product_packaging.qty
        self.sale.order_line[0].product_packaging_id = self.product_packaging.id
        self.sale.order_line[0].product_packaging_qty = 4
        wizard = self._get_wizard(
            self.saleblock_user,
            self.sale.with_user(self.saleblock_user.id).action_confirm(),
        )
        self.assertEqual(len(wizard.sale_line_block_ids), 1)
        # Wizard: Adjust Packaging Quantities
        wizard.action_adjust_packaging_quantity()
        self.assertEqual(self.sale.order_line[0].product_uom_qty, 1)
        self.assertEqual(self.sale.order_line[0].product_packaging_qty, 2)
        # No Block: 1 Unit (2 Packagings) in stock
        self.sale.with_user(self.saleblock_user.id).action_confirm()
        self.assertNotEqual(self.sale.state, "draft")

    def test_sale_move_to_new_order(self):
        """Test Wizard Moving to New Order."""
        self.company.sale_line_block_allowed_groups = False
        self.company.sale_line_field_block = self.f_qty_today
        # Block: No 4 Units in stock
        self.sale.order_line[0].product_uom = self.env.ref("uom.product_uom_unit").id
        self.sale.order_line[0].product_uom_qty = 4
        wizard = self._get_wizard(
            self.saleblock_user,
            self.sale.with_user(self.saleblock_user.id).action_confirm(),
        )
        self.assertEqual(len(wizard.sale_line_block_ids), 1)
        # Wizard: Move to new order
        new_orders = wizard.action_move_to_new_order()
        self.assertEqual(len(self.sale.order_line), 0)
        self.assertEqual(len(new_orders.order_line), 1)
