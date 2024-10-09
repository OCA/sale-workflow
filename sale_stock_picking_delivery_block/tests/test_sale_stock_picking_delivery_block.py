# Copyright 2022 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form, common


class TestSaleStockPickingDeliveryBlock(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.so_model = cls.env["sale.order"]
        cls.sol_model = cls.env["sale.order.line"]
        cls.test_partner = cls.env["res.partner"].create(
            {"name": "Foo", "email": "foo@dot.com"}
        )

        # Create product:
        prod_dict = {
            "name": "Demo product",
            "type": "product",
        }
        product = cls.env["product.product"].create(prod_dict)
        warehouse = cls.env["stock.warehouse"].search([], limit=1)
        cls.env["stock.quant"]._update_available_quantity(
            product, warehouse.wh_input_stock_loc_id, 100
        )
        # Create Sale order:
        cls.sale_order_no_block = cls.so_model.create(
            {
                "partner_id": cls.test_partner.id,
                "block_delivery": False,
            }
        )
        cls.sale_order_block = cls.so_model.create(
            {
                "partner_id": cls.test_partner.id,
                "block_delivery": True,
            }
        )
        # Create Sale order lines
        cls.sale_order_line_1 = cls.sol_model.create(
            {
                "order_id": cls.sale_order_no_block.id,
                "product_id": product.id,
                "product_uom_qty": 1.0,
            }
        )
        cls.sale_order_line_2 = cls.sol_model.create(
            {
                "order_id": cls.sale_order_block.id,
                "product_id": product.id,
                "product_uom_qty": 1.0,
            }
        )

    def test_check_sale_no_block(self):
        no_block_so = self.sale_order_no_block
        no_block_so.action_confirm()
        pick = no_block_so.picking_ids[0]
        self.assertNotEqual(pick, False, "A delivery should have been made")
        self.assertNotEqual(pick.block_delivery, True, "Delivery should not be blocked")

    def test_check_sale_block(self):
        block_so = self.sale_order_block
        block_so.action_confirm()
        pick_blocked = block_so.picking_ids[0]
        self.assertNotEqual(pick_blocked, False, "A delivery should have been made")
        self.assertNotEqual(
            pick_blocked.block_delivery, False, "Delivery should be blocked"
        )

    def test_check_release_sale_block(self):
        block_so = self.sale_order_block
        block_so.action_confirm()
        pick_blocked = block_so.picking_ids[0]
        self.assertNotEqual(pick_blocked, False, "A delivery should have been made")
        self.assertNotEqual(
            pick_blocked.block_delivery, False, "Delivery should be blocked"
        )
        # We cannot confirm the picking
        release_wiz = self.env["sale.release.delivery.wizard"].create(
            {"sale_id": block_so.id}
        )

        wiz_form = Form(release_wiz)
        wiz_form.log_reason = "Test"
        wiz_form.save()
        release_wiz.action_release_delivery()
        self.assertNotEqual(
            pick_blocked.block_delivery, True, "Delivery should not be blocked"
        )
