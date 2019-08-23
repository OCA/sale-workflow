# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.sale.tests.test_sale_common import TestSale
from odoo.exceptions import UserError
from datetime import datetime

class TestSaleStock(TestSale):
    def test_00_sale_manual_delivery(self):
        """
        Test SO's manual delivery
        """
        self.partner = self.env.ref("base.res_partner_1")
        self.product = self.env.ref("product.product_delivery_01")
        self.env['stock.change.product.qty'].create(
            {
                'product_id': self.product.id,
                'new_quantity': 10,
            },
        ).change_product_qty()
        so_vals = {
            "partner_id": self.partner.id,
            "partner_invoice_id": self.partner.id,
            "partner_shipping_id": self.partner.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": self.product.name,
                        "product_id": self.product.id,
                        "product_uom_qty": 5.0,
                        "product_uom": self.product.uom_id.id,
                        "price_unit": self.product.list_price,
                    },
                )
            ],
            "pricelist_id": self.env.ref("product.list0").id,
            "manual_delivery": True,
        }
        self.so = self.env["sale.order"].create(so_vals)

        # confirm our standard so, check the picking
        self.so.action_confirm()

        self.assertFalse(
            self.so.picking_ids,
            'Sale Manual Delivery: no \
            picking should be created for "manual delivery" orders',
        )

        # create a manual delivery for all ordered quantity
        wizard = self.env["manual.delivery"].create(
            {
                "order_id": self.so.id,
                "carrier_id": self.so.carrier_id.id,
                "date_planned": datetime.now(),
            }
        )
        wizard.onchange_order_id()
        wiz_act = self.env.ref(
            "sale_manual_delivery.action_wizard_manual_delivery"
        ).read()[0]
        wiz_act["res_id"] = wizard.id
        wiz = self.env[wiz_act["res_model"]].browse(wiz_act["res_id"])
        for line in wiz.line_ids:
            line.to_ship_qty=line.ordered_qty
        wiz.record_picking()
        # check picking is created
        self.assertTrue(
            self.so.picking_ids,
            'Sale Manual Delivery: picking \
            should be created after "manual delivery" wizard call',
        )

        # create a manual delivery, nothing left to ship
        wizard = self.env["manual.delivery"].create(
            {
                "order_id": self.so.id,
                "carrier_id": self.so.carrier_id.id,
                "date_planned": datetime.now(),
            }
        )
        wizard.onchange_order_id()
        wiz_act = self.env.ref(
            "sale_manual_delivery.action_wizard_manual_delivery"
        ).read()[0]
        wiz_act["res_id"] = wizard.id
        wiz = self.env[wiz_act["res_model"]].browse(wiz_act["res_id"])
        self.assertFalse(
            wiz.line_ids,
            "Sale Manual Delivery: After picking \
            creation for all products, no lines should be left in the wizard",
        )
        wiz.record_picking()
        self.assertEqual(
            len(self.so.picking_ids),
            1.0,
            "Sale Manual \
            Delivery: picking number should be 1.0 instead of %s as all qty \
            has been already created in a picking"
            % len(self.so.picking_ids),
        )

        # deliver completely
        pick = self.so.picking_ids
        pick.action_assign()
        pick.invalidate_cache()
        pick.move_line_ids.write({"qty_done": 5})
        pick.action_done()

        # Check quantity delivered
        del_qty = sum(sol.qty_delivered for sol in self.so.order_line)
        self.assertEqual(
            del_qty,
            5.0,
            "Sale Stock: delivered quantity should \
            be 5.0 instead of %s after complete delivery"
            % del_qty,
        )

    def test_01_sale_standard_delivery(self):
        """
        Test SO's standard delivery
        """
        self.partner = self.env.ref("base.res_partner_1")
        self.product = self.env.ref("product.product_delivery_01")
        self.env['stock.change.product.qty'].create(
            {
                'product_id': self.product.id,
                'new_quantity': 10,
            },
        ).change_product_qty()
        so_vals = {
            "partner_id": self.partner.id,
            "partner_invoice_id": self.partner.id,
            "partner_shipping_id": self.partner.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": self.product.name,
                        "product_id": self.product.id,
                        "product_uom_qty": 5.0,
                        "product_uom": self.product.uom_id.id,
                        "price_unit": self.product.list_price,
                    },
                )
            ],
            "pricelist_id": self.env.ref("product.list0").id,
            "manual_delivery": False,
        }
        self.so = self.env["sale.order"].create(so_vals)

        # confirm our standard so, check the picking
        self.so.action_confirm()
        self.assertTrue(
            self.so.picking_ids,
            'Sale Manual Delivery: \
            picking should be created for "standard delivery" orders',
        )

        # deliver completely
        pick = self.so.picking_ids
        pick.action_assign()
        pick.invalidate_cache()
        pick.move_line_ids.write({"qty_done": 5})
        pick.action_done()

        # Check quantity delivered
        del_qty = sum(sol.qty_delivered for sol in self.so.order_line)
        self.assertEqual(
            del_qty,
            5.0,
            "Sale Stock: delivered quantity should \
            be 5.0 instead of %s after complete delivery"
            % del_qty,
        )

    def test_02_sale_various_manual_delivery(self):
        """
        Test SO's various manual delivery
        """
        self.partner = self.env.ref("base.res_partner_1")
        self.product = self.env.ref("product.product_delivery_01")
        self.env['stock.change.product.qty'].create(
            {
                'product_id': self.product.id,
                'new_quantity': 10,
            },
        ).change_product_qty()
        so_vals = {
            "partner_id": self.partner.id,
            "partner_invoice_id": self.partner.id,
            "partner_shipping_id": self.partner.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": self.product.name,
                        "product_id": self.product.id,
                        "product_uom_qty": 5.0,
                        "product_uom": self.product.uom_id.id,
                        "price_unit": self.product.list_price,
                    },
                )
            ],
            "pricelist_id": self.env.ref("product.list0").id,
            "manual_delivery": True,
        }
        self.so = self.env["sale.order"].create(so_vals)

        # confirm our standard so, check the picking
        self.so.action_confirm()
        self.assertFalse(
            self.so.picking_ids,
            'Sale Manual Delivery: no \
            picking should be created for "manual delivery" orders',
        )

        # create a manual delivery for part of ordered quantity
        wizard = self.env["manual.delivery"].create(
            {
                "order_id": self.so.id,
                "carrier_id": self.so.carrier_id.id,
                "date_planned": datetime.now(),
            }
        )
        wizard.onchange_order_id()
        wiz_act = self.env.ref(
            "sale_manual_delivery.action_wizard_manual_delivery"
        ).read()[0]
        wiz_act["res_id"] = wizard.id
        wiz = self.env[wiz_act["res_model"]].browse(wiz_act["res_id"])
        for line in wiz.line_ids:
            line.to_ship_qty=2.0
        wiz.record_picking()
        # check picking is created
        self.assertTrue(
            self.so.picking_ids,
            'Sale Manual Delivery: picking \
            should be created after "manual delivery" wizard call',
        )


        # deliver completely
        pick = self.so.picking_ids
        pick.action_assign()
        pick.invalidate_cache()
        pick.move_line_ids.write({"qty_done": 2})
        pick.action_done()

        # Check quantity delivered
        del_qty = sum(sol.qty_delivered for sol in self.so.order_line)
        self.assertEqual(
            del_qty,
            2.0,
            "Sale Stock: delivered quantity should \
            be 2.0 instead of %s after complete delivery"
            % del_qty,
        )

        # create a manual delivery, 3.0 left to ship
        wizard = self.env["manual.delivery"].create(
            {
                "order_id": self.so.id,
                "carrier_id": self.so.carrier_id.id,
                "date_planned": datetime.now(),
            }
        )
        wizard.onchange_order_id()
        wiz_act = self.env.ref(
            "sale_manual_delivery.action_wizard_manual_delivery"
        ).read()[0]
        wiz_act["res_id"] = wizard.id
        wiz = self.env[wiz_act["res_model"]].browse(wiz_act["res_id"])
        for line in wiz.line_ids:
            line.to_ship_qty=3.0
        wiz.record_picking()
        self.assertEqual(
            len(self.so.picking_ids),
            2.0,
            "Sale Manual \
            Delivery: picking number should be 2.0 instead of %s as all qty \
            has been already created in a picking"
            % len(self.so.picking_ids),
        )

        # deliver completely last one
        for pick in self.so.picking_ids:
            if pick.state != "done":
                pick.action_assign()
                pick.invalidate_cache()
                pick.move_line_ids.write({"qty_done": 3})
                pick.action_done()

        # Check quantity delivered
        del_qty = sum(sol.qty_delivered for sol in self.so.order_line)
        self.assertEqual(
            del_qty,
            5.0,
            "Sale Stock: delivered quantity should \
            be 5.0 instead of %s after complete delivery"
            % del_qty,
        )
