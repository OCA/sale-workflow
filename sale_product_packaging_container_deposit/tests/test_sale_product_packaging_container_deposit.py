# Copyright 2023 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import UserError
from odoo.tests import Form

from odoo.addons.product_packaging_container_deposit.tests.common import Common


class TestSaleProductPackagingContainerDeposit(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order = cls.env["sale.order"].create(
            {
                "company_id": cls.env.company.id,
                "partner_id": cls.env.ref("base.res_partner_12").id,
            }
        )

    def test_confirmed_sale_product_packaging_container_deposit_quantities(self):
        """Container deposit is added on confirmed orders"""
        self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order.id,
                "name": self.product_a.name,
                "product_id": self.product_a.id,
                "product_uom_qty": 50,
            }
        )
        self.sale_order.action_confirm()
        deposit_lines = self.sale_order.order_line.filtered(
            lambda ol: ol.product_id
            in self.product_a.mapped(
                "packaging_ids.package_type_id.container_deposit_product_id"
            )
        )
        self.assertEqual(len(deposit_lines), 1)

    def test_sale_product_packaging_container_deposit_quantities_case1(self):
        """
        Case 1: Product A | qty = 280. Result:
                280 // 240 = 1 => add SO line for 1 Pallet
                280 // 24 (biggest PACK) => add SO line for 11 boxes of 24
        """
        self.env["sale.order.line"].create(
            [
                {
                    "order_id": self.sale_order.id,
                    "name": self.product_a.name,
                    "product_id": self.product_a.id,
                    "product_uom_qty": 280,
                },
                {
                    "order_id": self.sale_order.id,
                    "name": self.product_c.name,
                    "product_id": self.product_c.id,
                    "product_uom_qty": 1,
                },
            ]
        )

        pallet_line = self.sale_order.order_line.filtered(
            lambda ol: ol.product_id == self.pallet
        )
        box_line = self.sale_order.order_line.filtered(
            lambda ol: ol.product_id == self.box
        )
        self.assertEqual(pallet_line.product_uom_qty, 1)
        self.assertEqual(box_line.product_uom_qty, 11)

    def test_sale_product_packaging_container_deposit_quantities_case2(self):
        """
        Case 2: Product A | qty = 280 and packaging=Box of 12. Result:
            280 // 240 = 1 => add SO line for 1 Pallet
            280 // 12 (forced packaging for Boxes) => add SO line for 23 boxes of 12
        """
        self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order.id,
                "name": self.product_a.name,
                "product_id": self.product_a.id,
                "product_uom_qty": 280,
                # Box of 12
                "product_packaging_id": self.packaging[0].id,
            },
        )
        # Filter lines with boxes
        box_lines = self.sale_order.order_line.filtered(
            lambda ol: ol.product_id == self.box
        )
        self.assertEqual(box_lines[0].product_uom_qty, 23)

    def test_sale_product_packaging_container_deposit_quantities_case3(self):
        """
        Case 3: Product A & Product B. Both have a deposit of 1 box of 24. Result:
                Only one line for 2 boxes of 24
        """
        self.env["sale.order.line"].create(
            [
                {
                    "order_id": self.sale_order.id,
                    "name": self.product_a.name,
                    "product_id": self.product_a.id,
                    "product_uom_qty": 24,
                },
                {
                    "order_id": self.sale_order.id,
                    "name": self.product_b.name,
                    "product_id": self.product_b.id,
                    "product_uom_qty": 24,
                },
            ]
        )
        box_lines = self.sale_order.order_line.filtered(
            lambda ol: ol.product_id == self.box
        )
        self.assertEqual(box_lines[0].product_uom_qty, 2)

    def test_sale_product_packaging_container_deposit_quantities_case4(self):
        """
        Case 4: Product A | qty = 24. Result:
                24 // 24 (biggest PACK) => add SO line for 1 box of 24
                Product A | Increase to 48. Result:
                48 // 24 (biggest PACK) =>  recompute previous SO line with 2 boxes of 24
                Add manually Product A container deposit (Box). Result:
                1 SO line with 2 boxes of 24 (System added)
                + 1 SO line with 1 box (manually added)
        """
        order_line = self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order.id,
                "name": self.product_a.name,
                "product_id": self.product_a.id,
                "product_uom_qty": 24,
            },
        )
        order_line.write({"product_uom_qty": 48})
        deposit_line = self.sale_order.order_line.filtered(
            lambda ol: ol.product_id
            in self.product_a.mapped(
                "packaging_ids.package_type_id.container_deposit_product_id"
            )
        )
        self.assertEqual(deposit_line.name, "Box")
        self.assertEqual(deposit_line.product_uom_qty, 2.0)

        # Add manually 1 box
        self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order.id,
                "name": self.package_type_box.container_deposit_product_id.name,
                "product_id": self.package_type_box.container_deposit_product_id.id,
                "product_uom_qty": 1,
            }
        )

        box_lines = self.sale_order.order_line.filtered(
            lambda ol: ol.product_id == self.box
        )
        self.assertEqual(box_lines[0].product_uom_qty, 2)
        self.assertEqual(box_lines[1].product_uom_qty, 1)

    def test_sale_product_packaging_container_deposit_quantities_case5(self):
        """
        Case 5: Product A | qty = 280 on confirmed order.
                Product A | Increase qty to 480. Result:
                480 // 240 = 1 => add SO line for 2 Pallet
                480 // 24 (biggest PACK) => add SO line for 20 boxes of 24
        """
        self.env["sale.order.line"].create(
            [
                {
                    "order_id": self.sale_order.id,
                    "name": self.product_a.name,
                    "product_id": self.product_a.id,
                    "product_uom_qty": 280,
                },
                {
                    "order_id": self.sale_order.id,
                    "name": self.product_c.name,
                    "product_id": self.product_c.id,
                    "product_uom_qty": 1,
                },
            ]
        )
        self.sale_order.action_confirm()
        self.sale_order.order_line[0].product_uom_qty = 480

        # Odoo standard try to propose a suitable product packaging.
        # We don't want it in that case
        self.sale_order.order_line[0].product_packaging_id = False

        pallet_line = self.sale_order.order_line.filtered(
            lambda ol: ol.product_id == self.pallet
        )
        box_line = self.sale_order.order_line.filtered(
            lambda ol: ol.product_id == self.box
        )
        self.assertEqual(pallet_line.product_uom_qty, 2)
        self.assertEqual(box_line.product_uom_qty, 20)

    def test_sale_product_packaging_container_deposit_quantities_case6(self):
        """
        Case 6: Product A | qty = 280 on confirmed order.
                Product A | qty_delivered = 280. Result:
                Delivered 1 Pallet
                Delivered 11 Boxes

        """
        self.env["sale.order.line"].create(
            [
                {
                    "order_id": self.sale_order.id,
                    "name": self.product_a.name,
                    "product_id": self.product_a.id,
                    "product_uom_qty": 280,
                },
            ]
        )
        self.sale_order.action_confirm()

        pick = self.sale_order.picking_ids
        pick.move_ids.write({"quantity_done": 280})
        pick.button_validate()

        pallet_line = self.sale_order.order_line.filtered(
            lambda ol: ol.product_id == self.pallet
        )
        box_line = self.sale_order.order_line.filtered(
            lambda ol: ol.product_id == self.box
        )
        self.assertEqual(pallet_line.qty_delivered, 1)
        self.assertEqual(box_line.qty_delivered, 11)

    def test_sale_product_packaging_container_deposit_quantities_case7(self):
        """
        Case 7.1: Product A | qty = 280 on confirmed order.
                Product A | Partial shipment (qty_delivered = 140). Result:
                Delivered 140 // 280 = 0 Pallet
                Delivered 140 // 24 = 5 Boxes
        Case 7.2: Product A | Increase delivered quantity (qty_delivered = 200). Result:

                Delivered 200 // 280 = 0 Pallet
                Delivered 200 // 24 = 5 Boxes
        """
        order_line = self.env["sale.order.line"].create(
            [
                {
                    "order_id": self.sale_order.id,
                    "name": self.product_a.name,
                    "product_id": self.product_a.id,
                    "product_uom_qty": 280,
                },
            ]
        )
        self.sale_order.action_confirm()
        pick = self.sale_order.picking_ids
        pick.move_ids.write({"quantity_done": 140})
        wiz_act = pick.button_validate()
        wiz = Form(
            self.env[wiz_act["res_model"]].with_context(**wiz_act["context"])
        ).save()
        wiz.process()

        pallet_line = self.sale_order.order_line.filtered(
            lambda ol: ol.product_id == self.pallet
        )
        box_line = self.sale_order.order_line.filtered(
            lambda ol: ol.product_id == self.box
        )
        (box_line | pallet_line).invalidate_cache()
        self.assertEqual(pallet_line.qty_delivered, 0)
        self.assertEqual(box_line.qty_delivered, 5)

        order_line.qty_delivered = 200
        self.assertEqual(pallet_line.qty_delivered, 0)
        self.assertEqual(box_line.qty_delivered, 8)

    def test_sale_product_packaging_container_deposit_quantities_case8(self):
        """Test add and delete container deposit lines"""
        sale_form = Form(self.env["sale.order"])
        sale_form.partner_id = self.sale_order.partner_id
        with sale_form.order_line.new() as line:
            line.product_id = self.product_a
            line.product_uom_qty = 280
        sale = sale_form.save()
        with sale_form.order_line.edit(0) as line:
            line.product_uom_qty = 10

        lines_to_delete = sale.order_line.filtered(
            lambda ol: ol.product_id == self.pallet or ol.product_id == self.box
        )
        with self._check_delete_after_commit(lines_to_delete):
            sale_form.save()

    def test_sale_product_packaging_container_deposit_quantities_case9(self):
        """
        Case 9: With locked order, Product A | qty = 280. Result:
                280 // 240 = 1 => add SO line for 1 Pallet
                280 // 24 (biggest PACK) => add SO line for 11 boxes of 24

        """
        self.env.user.groups_id += self.env.ref("sale.group_auto_done_setting")
        self.env["sale.order.line"].with_context(
            skip_update_container_deposit=True
        ).create(
            [
                {
                    "order_id": self.sale_order.id,
                    "name": self.product_a.name,
                    "product_id": self.product_a.id,
                    "product_uom_qty": 280,
                },
            ]
        )
        # Not have any container deposit product
        self.assertEqual(len(self.sale_order.order_line), 1)
        self.sale_order.action_confirm()

        # For now, the SO has been locked, so we can't modify the lines
        with self.assertRaisesRegex(
            UserError,
            "It is forbidden to modify the following fields in a locked order:\nQuantity",
        ):
            self.sale_order.order_line.write(
                {
                    "product_uom_qty": 3,
                }
            )
        # With the "update_order_container_deposit_quantity" context
        # We can update order container deposit quantity on locked order
        self.sale_order.with_context(
            skip_update_container_deposit=False
        ).update_order_container_deposit_quantity()

        # Check on locked order
        self.assertEqual(len(self.sale_order.order_line), 3)

        pallet_line = self.sale_order.order_line.filtered(
            lambda ol: ol.product_id == self.pallet
        )
        box_line = self.sale_order.order_line.filtered(
            lambda ol: ol.product_id == self.box
        )

        self.assertEqual(pallet_line.product_uom_qty, 1)
        self.assertEqual(box_line.product_uom_qty, 11)
