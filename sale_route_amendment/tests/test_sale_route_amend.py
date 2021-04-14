# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form
from odoo.tests.common import SavepointCase


class TestSaleOrderLineUpdateRoute(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.move_obj = cls.env["stock.move"]
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.product = cls.env.ref("product.product_product_4")
        cls.product_2 = cls.env.ref("product.product_product_5")
        cls.product_service = cls.env.ref("product.product_product_1")
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.loc_customer = cls.env.ref("stock.stock_location_customers")
        cls.loc_supplier = cls.env.ref("stock.stock_location_suppliers")
        cls.loc_stock = cls.env.ref("stock.stock_location_stock")
        vals = {
            "name": "DROP SHIPPING",
            "sequence_id": cls.env.ref("stock.seq_picking_internal").id,
            "code": "outgoing",
            "warehouse_id": cls.warehouse.id,
            "sequence_code": "DROP",
            "default_location_src_id": cls.loc_supplier.id,
            "default_location_dest_id": cls.loc_customer.id,
        }
        pick_type_drop_shipping = cls.env["stock.picking.type"].create(vals)

        vals = {
            "name": "DROP SHIP",
            "sequence": 1,
            "sale_selectable": True,
            "rule_ids": [
                (
                    0,
                    0,
                    {
                        "name": "OUTPUT => Customers",
                        "action": "pull",
                        "location_src_id": cls.loc_supplier.id,
                        "location_id": cls.loc_customer.id,
                        "picking_type_id": pick_type_drop_shipping.id,
                        "procure_method": "make_to_stock",
                    },
                )
            ],
        }
        cls.route_drop = cls.env["stock.location.route"].create(vals)
        qty_wizard = cls.env["stock.change.product.qty"].create(
            {
                "product_id": cls.product_2.id,
                "product_tmpl_id": cls.product_2.product_tmpl_id.id,
                "new_quantity": 1.0,
            }
        )
        qty_wizard.change_product_qty()

    def test_amend_route(self):
        """
            Create and confirm a sale order
            The created move will use the default route Stock > Customers

            Launch the wizard to update the route and select the drop shipping
            route.

            A new move is created from Vendors > Customers
        """
        so = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "warehouse_id": self.warehouse.id,
                "order_line": [
                    (0, 0, {"product_id": self.product.id, "product_uom_qty": 1.0})
                ],
            }
        )
        so.action_confirm()

        picking = so.picking_ids.filtered(lambda p: p.location_id == self.loc_stock)
        move = picking.move_lines
        self.assertTrue(move)

        wiz_obj = self.env["sale.order.line.route.amend"].with_context(active_id=so.id)
        wizard_form = Form(wiz_obj)
        wizard_form.route_id = self.route_drop
        wizard = wizard_form.save()
        wizard.update_route()
        domain = [
            ("group_id", "=", so.procurement_group_id.id),
            ("location_id", "=", self.loc_supplier.id),
            ("state", "!=", "cancel"),
        ]
        move = self.move_obj.search(domain, limit=1)
        self.assertTrue(move)

    def test_amend_route_multi_product(self):
        """
            Create and confirm a sale order with several product lines
            The created move will use the default route Stock > Customers

            Launch the wizard to update the route and select the drop shipping
            route.

            A new move is created from Vendors > Customers
        """
        so = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "warehouse_id": self.warehouse.id,
                "order_line": [
                    (0, 0, {"product_id": self.product.id, "product_uom_qty": 1.0}),
                    (0, 0, {"product_id": self.product_2.id, "product_uom_qty": 1.0}),
                ],
            }
        )
        so.action_confirm()

        picking = so.picking_ids.filtered(lambda p: p.location_id == self.loc_stock)
        moves = picking.move_lines
        self.assertTrue(moves)

        # Confirm a move quantity
        move_to_confirm = moves.filtered(lambda m: m.product_id == self.product_2)

        move_to_confirm.move_line_ids.qty_done = 1.0
        picking.action_done()

        self.assertEquals(
            "done", picking.state,
        )

        wiz_obj = self.env["sale.order.line.route.amend"].with_context(active_id=so.id)
        wizard_form = Form(wiz_obj)
        wizard_form.route_id = self.route_drop
        wizard = wizard_form.save()
        wizard.update_route()
        domain = [
            ("product_id", "=", self.product.id),
            ("group_id", "=", so.procurement_group_id.id),
            ("location_id", "=", self.loc_supplier.id),
            ("state", "!=", "cancel"),
        ]
        move = self.move_obj.search(domain, limit=1)
        self.assertTrue(move)

    def test_amend_route_warning(self):
        """
            Create and confirm a sale order
            The created move will use the default route Stock > Customers

            Update the qty_done on move

            Launch the wizard to update the route and select the drop shipping
            route.

            A new move is created from Vendors > Customers
        """
        so = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "warehouse_id": self.warehouse.id,
                "order_line": [
                    (0, 0, {"product_id": self.product.id, "product_uom_qty": 1.0})
                ],
            }
        )
        so.action_confirm()
        picking = so.picking_ids.filtered(lambda p: p.location_id == self.loc_stock)
        move = picking.move_lines

        self.assertTrue(move)
        move.picking_id.action_assign()
        self.assertEqual(
            "assigned", move.state,
        )
        self.assertEqual(
            1, len(move.move_line_ids),
        )
        wiz_obj = self.env["sale.order.line.route.amend"].with_context(active_id=so.id)
        wizard_form = Form(wiz_obj)
        wizard_form.route_id = self.route_drop
        wizard = wizard_form.save()
        self.assertFalse(wizard.warning)

        move.move_line_ids.qty_done = 1.0

        wiz_obj = self.env["sale.order.line.route.amend"].with_context(active_id=so.id)
        wizard_form = Form(wiz_obj)
        wizard_form.route_id = self.route_drop
        wizard = wizard_form.save()
        self.assertTrue(wizard.warning)

    def test_amend_route_service(self):
        """
            Create and confirm a sale order with a service product
            The created move will use the default route Stock > Customers

            Launch the wizard to update the route and select the drop shipping
            route.

            Check if only one sale line is selected in wizard
        """
        so = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "warehouse_id": self.warehouse.id,
                "order_line": [
                    (0, 0, {"product_id": self.product.id, "product_uom_qty": 1.0}),
                    (
                        0,
                        0,
                        {"product_id": self.product_service.id, "product_uom_qty": 1.0},
                    ),
                ],
            }
        )
        so.action_confirm()

        picking = so.picking_ids.filtered(lambda p: p.location_id == self.loc_stock)
        move = picking.move_lines
        self.assertTrue(move)
        move.picking_id.action_assign()
        self.assertEqual(
            "assigned", move.state,
        )
        self.assertEqual(
            1, len(move.move_line_ids),
        )

        wiz_obj = self.env["sale.order.line.route.amend"].with_context(active_id=so.id)
        wizard_form = Form(wiz_obj)
        wizard_form.route_id = self.route_drop
        wizard = wizard_form.save()
        self.assertEqual(
            1, len(wizard.order_line_ids),
        )
        self.assertFalse(wizard.warning)
