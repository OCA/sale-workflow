# Copyright 2025 360ERP (https://www.360erp.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests.common import TransactionCase


class TestSalePhantomBomProcurementMultiLine(TransactionCase):
    """
    Tests Phantom BoM explosion for Kits selected on SO Lines.
    Focuses on a scenario with multiple lines for the same kit product,
    each specifying a different phantom BoM referencing the same component,
    to ensure component quantities are correctly exploded and aggregated
    within the resulting Stock Picking moves.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )
        cls.company = cls.env.company

        # Required groups
        cls.env.user.groups_id += cls.env.ref("stock.group_adv_location")
        cls.env.user.groups_id += cls.env.ref("sale_mrp_bom.sale_mrp_bom_group")

        # Ensure MTO Route is Active
        cls.mto_route = cls.env.ref(
            "stock.route_warehouse0_mto", raise_if_not_found=True
        )
        if not cls.mto_route.active:
            cls.mto_route.action_unarchive()

        # Products
        cls.product_mtokit = cls.env["product.product"].create(
            [
                {
                    "name": "MTOKIT",
                    "type": "consu",
                    "route_ids": [(6, 0, [cls.mto_route.id])],
                    "categ_id": cls.env.ref("product.product_category_all").id,
                }
            ]
        )
        cls.product_mtocomp = cls.env["product.product"].create(
            [
                {
                    "name": "MTOCOMP",
                    "type": "consu",
                    "route_ids": [],
                    "categ_id": cls.env.ref("product.product_category_all").id,
                }
            ]
        )

        # BoMs (Phantom)
        cls.bom_kit1 = cls.env["mrp.bom"].create(
            [
                {
                    "product_tmpl_id": cls.product_mtokit.product_tmpl_id.id,
                    "product_qty": 1.0,
                    "type": "phantom",
                    "code": "KIT1",
                }
            ]
        )
        # BoM Line 1: 1 x MTOCOMP
        cls.env["mrp.bom.line"].create(
            [
                {
                    "bom_id": cls.bom_kit1.id,
                    "product_id": cls.product_mtocomp.id,
                    "product_qty": 1,
                }
            ]
        )
        cls.bom_kit2 = cls.env["mrp.bom"].create(
            [
                {
                    "product_tmpl_id": cls.product_mtokit.product_tmpl_id.id,
                    "product_qty": 1.0,
                    "type": "phantom",
                    "code": "KIT2",
                }
            ]
        )
        # BoM Line 2: 2 x MTOCOMP
        cls.env["mrp.bom.line"].create(
            [
                {
                    "bom_id": cls.bom_kit2.id,
                    "product_id": cls.product_mtocomp.id,
                    "product_qty": 2,
                }
            ]
        )

        cls.partner = cls.env.ref("base.res_partner_2")  # Customer
        cls.warehouse = cls.env.ref("stock.warehouse0")

    def _create_sale_order(self, partner):
        return self.env["sale.order"].create(
            [
                {
                    "partner_id": partner.id,
                    "partner_invoice_id": partner.id,
                    "partner_shipping_id": partner.id,
                    "warehouse_id": self.warehouse.id,
                }
            ]
        )

    def _create_sale_order_line(self, sale_order, product, qty, bom):
        sol = self.env["sale.order.line"].create(
            [
                {
                    "order_id": sale_order.id,
                    "product_id": product.id,
                    "product_uom_qty": qty,
                    "bom_id": bom.id,
                    "product_uom": product.uom_id.id,
                    "price_unit": 1,
                }
            ]
        )
        return sol

    def test_phantom_bom_explosion_multi_line_same_component(self):
        """
        Test SO with 2 lines for MTOKIT (phantom): Line 1 uses KIT1 (1 comp),
        Line 2 uses KIT2 (2 comps).
        Verify that the resulting delivery picking moves contain lines for MTO_COMP
        with correctly aggregated quantities based on the phantom BoM explosion.
        """
        # Create SO
        so = self._create_sale_order(self.partner)
        qty_line1 = 5
        qty_line2 = 3

        # Line 1: 5 x MTOKIT using KIT1 (-> 5 * 1 = 5 MTO_COMP)
        self._create_sale_order_line(so, self.product_mtokit, qty_line1, self.bom_kit1)
        # Line 2: 3 x MTOKIT using KIT2 (-> 3 * 2 = 6 MTO_COMP)
        self._create_sale_order_line(so, self.product_mtokit, qty_line2, self.bom_kit2)

        # Confirm the Sale Order - This triggers the delivery order creation
        # and the phantom BoM explosion for the delivery moves.
        so.action_confirm()

        # Find the picking associated with the Sale Order
        pickings = so.picking_ids
        self.assertEqual(
            len(pickings),
            1,
            f"Expected one picking for {so.name}, found {len(pickings)}",
        )
        picking = pickings[0]

        # Find stock moves within this picking
        moves = picking.move_ids

        # Verify no moves for the kit itself (it's phantom)
        kit_product_moves = moves.filtered(
            lambda m: m.product_id == self.product_mtokit
        )
        self.assertFalse(
            kit_product_moves,
            "No stock move line should be created for the parent kit product (MTOKIT).",
        )

        # Find the moves specifically for the component within this picking
        comp_product_moves = moves.filtered(
            lambda m: m.product_id == self.product_mtocomp
        )
        self.assertTrue(
            comp_product_moves,
            f"Stock move lines for {self.product_mtocomp.name} should be created.",
        )

        # Calculate expected *total* component quantity based on BoMs
        expected_comp_qty_line1 = (
            qty_line1
            * self.bom_kit1.bom_line_ids.filtered(
                lambda bl: bl.product_id == self.product_mtocomp
            ).product_qty
        )
        expected_comp_qty_line2 = (
            qty_line2
            * self.bom_kit2.bom_line_ids.filtered(
                lambda bl: bl.product_id == self.product_mtocomp
            ).product_qty
        )
        expected_total_qty = (
            expected_comp_qty_line1 + expected_comp_qty_line2
        )  # Should be 5 * 1 + 3 * 2 = 11

        # Verify the total quantity demanded in the generated stock moves
        # Check the initial demand planned for the picking
        actual_total_move_qty = sum(comp_product_moves.mapped("product_uom_qty"))
        self.assertEqual(
            actual_total_move_qty,
            expected_total_qty,
            f"MTO_COMP: expected {expected_total_qty}, got {actual_total_move_qty}.",
        )
