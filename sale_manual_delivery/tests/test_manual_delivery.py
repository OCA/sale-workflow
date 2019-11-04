# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.sale.tests.test_sale_common import TestSale
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DF


class TestSaleStock(TestSale):
    def _update_product_qty(self, product, quantity):
        """Update Product quantity."""
        product_qty = self.env["stock.change.product.qty"].create(
            {"product_id": product.id, "new_quantity": quantity, }
        )
        product_qty.change_product_qty()
        return product_qty

    def test_00_sale_manual_delivery(self):
        """
        Test SO's manual delivery
        """
        self.partner = self.env.ref("base.res_partner_1")
        self.product = self.env.ref("product.product_delivery_01")
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
        wizard = (
            self.env["manual.delivery"]
            .with_context(
                {
                    "active_model": "sale.order.line",
                    "active_ids": self.so.order_line.ids,
                }
            )
            .create({})
        )
        wizard.onchange_line_ids()
        wiz_act = self.env.ref(
            "sale_manual_delivery.action_wizard_manual_delivery"
        ).read()[0]
        wiz_act["res_id"] = wizard.id
        wiz = self.env[wiz_act["res_model"]].browse(wiz_act["res_id"])
        wiz.record_picking()
        # check picking is created
        self.assertTrue(
            self.so.picking_ids,
            'Sale Manual Delivery: picking \
            should be created after "manual delivery" wizard call',
        )

        # create a manual delivery, nothing left to ship
        wizard = (
            self.env["manual.delivery"]
            .with_context(
                {
                    "active_model": "sale.order.line",
                    "active_ids": self.so.order_line.ids,
                }
            )
            .create({})
        )
        wizard.onchange_line_ids()
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
        pick.force_assign()
        pick.pack_operation_product_ids.write({"qty_done": 5})
        pick.do_new_transfer()

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
        pick.force_assign()
        pick.pack_operation_product_ids.write({"qty_done": 5})
        pick.do_new_transfer()

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
        wizard = (
            self.env["manual.delivery"]
            .with_context(
                {
                    "active_model": "sale.order.line",
                    "active_ids": self.so.order_line.ids,
                }
            )
            .create({})
        )
        wizard.onchange_line_ids()
        wiz_act = self.env.ref(
            "sale_manual_delivery.action_wizard_manual_delivery"
        ).read()[0]
        wiz_act["res_id"] = wizard.id
        wiz = self.env[wiz_act["res_model"]].browse(wiz_act["res_id"])
        for line in wiz.line_ids:
            line.to_ship_qty = 2.0
        wiz.record_picking()
        # check picking is created
        self.assertTrue(
            self.so.picking_ids,
            'Sale Manual Delivery: picking \
            should be created after "manual delivery" wizard call',
        )

        # deliver completely
        pick = self.so.picking_ids
        pick.force_assign()
        pick.pack_operation_product_ids.write({"qty_done": 2})
        pick.do_new_transfer()

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
        wizard = (
            self.env["manual.delivery"]
            .with_context(
                {
                    "active_model": "sale.order.line",
                    "active_ids": self.so.order_line.ids,
                }
            )
            .create({})
        )
        wizard.onchange_line_ids()
        wiz_act = self.env.ref(
            "sale_manual_delivery.action_wizard_manual_delivery"
        ).read()[0]
        wiz_act["res_id"] = wizard.id
        wiz = self.env[wiz_act["res_model"]].browse(wiz_act["res_id"])
        for line in wiz.line_ids:
            line.to_ship_qty = 3.0
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
                pick.force_assign()
                pick.pack_operation_product_ids.write({"qty_done": 3})
                pick.do_new_transfer()

        # Check quantity delivered
        del_qty = sum(sol.qty_delivered for sol in self.so.order_line)
        self.assertEqual(
            del_qty,
            5.0,
            "Sale Stock: delivered quantity should \
            be 5.0 instead of %s after complete delivery"
            % del_qty,
        )

    def test_03_sale_selected_lines(self):
        """
        Test SO's various manual delivery
        """
        self.partner = self.env.ref("base.res_partner_1")
        self.product = self.env.ref("product.product_delivery_01")
        self.product2 = self.env.ref("product.product_delivery_02")
        self.product3 = self.env.ref("product.product_order_01")
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
                        "product_uom_qty": 1.0,
                        "product_uom": self.product.uom_id.id,
                        "price_unit": self.product.list_price,
                    },
                )
            ],
            "pricelist_id": self.env.ref("product.list0").id,
            "manual_delivery": True,
        }
        self.so1 = self.env["sale.order"].create(so_vals)
        so_vals = {
            "partner_id": self.partner.id,
            "partner_invoice_id": self.partner.id,
            "partner_shipping_id": self.partner.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": self.product2.name,
                        "product_id": self.product2.id,
                        "product_uom_qty": 2.0,
                        "product_uom": self.product2.uom_id.id,
                        "price_unit": self.product2.list_price,
                    },
                )
            ],
            "pricelist_id": self.env.ref("product.list0").id,
            "manual_delivery": True,
        }
        self.so2 = self.env["sale.order"].create(so_vals)

        so_vals = {
            "partner_id": self.partner.id,
            "partner_invoice_id": self.partner.id,
            "partner_shipping_id": self.partner.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": self.product3.name,
                        "product_id": self.product.id,
                        "product_uom_qty": 3.0,
                        "product_uom": self.product3.uom_id.id,
                        "price_unit": self.product3.list_price,
                    },
                )
            ],
            "pricelist_id": self.env.ref("product.list0").id,
            "manual_delivery": True,
        }
        self.so3 = self.env["sale.order"].create(so_vals)

        # confirm our standard so, check the picking
        self.so1.action_confirm()
        self.so2.action_confirm()
        self.so3.action_confirm()
        some_lines = self.so1.order_line + self.so3.order_line
        all_lines = (
            self.so1.order_line + self.so2.order_line + self.so3.order_line
        )
        # create a manual delivery for part of ordered quantity
        wizard = (
            self.env["manual.delivery"]
            .with_context(
                {
                    "active_model": "sale.order.line",
                    "active_ids": some_lines.ids,
                }
            )
            .create({})
        )
        wizard.onchange_line_ids()
        wiz_act = self.env.ref(
            "sale_manual_delivery.action_wizard_manual_delivery"
        ).read()[0]
        wiz_act["res_id"] = wizard.id
        wiz = self.env[wiz_act["res_model"]].browse(wiz_act["res_id"])
        self.assertEqual(sum(wiz.line_ids.mapped("to_ship_qty")), 4.0)
        wiz.record_picking()
        # check picking is created
        self.assertTrue(
            self.so1.picking_ids,
            'Sale Manual Delivery: picking \
            should be created after "manual delivery" wizard call',
        )
        self.assertFalse(
            self.so2.picking_ids,
            'Sale Manual Delivery: picking \
            should not be created after "manual delivery" wizard call',
        )
        # test action undelivered
        # self.env['sale.order.line'].search([])._compute_existing_qty()
        undelivered = (
            self.env["sale.order.line"]
            .search(
                [("pending_qty_to_deliver", "=", True), ("state", "=", "sale")]
            )
            .filtered(lambda s: s.id in all_lines.ids)
        )
        self.assertEqual(
            undelivered,
            self.so2.order_line,
            "Bad pending qty to deliver filter",
        )

    def test_03_sale_multi_delivery(self):
        self.product = self.env.ref("product.product_delivery_01")
        self.product_2 = self.env.ref("product.product_delivery_02")
        self._update_product_qty(self.product, 10.0)
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
                        "product_uom_qty": 10.0,
                        "product_uom": self.product.uom_id.id,
                        "price_unit": self.product.list_price,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": self.product_2.name,
                        "product_id": self.product_2.id,
                        "product_uom_qty": 10.0,
                        "product_uom": self.product_2.uom_id.id,
                        "price_unit": self.product_2.list_price,
                    },
                ),
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
        date_now = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        wizard = (
            self.env["manual.delivery"]
            .with_context(
                {
                    "active_model": "sale.order.line",
                    "active_ids": self.so.order_line[0].ids,
                }
            )
            .create(
                {"carrier_id": self.so.carrier_id.id, "date_planned": date_now}
            )
        )
        wizard.onchange_line_ids()
        for line in wizard.line_ids:
            line.to_ship_qty = 2.0
        wizard.record_picking()
        # check picking is created
        self.assertEqual(
            len(self.so.picking_ids),
            1,
            'Sale Manual Delivery: picking should be created after "manual'
            ' delivery" wizard call',
        )
        first_picking = self.so.picking_ids
        self.assertEqual(
            datetime.strptime(first_picking.min_date, DF).replace(
                hour=0, minute=0, second=0, microsecond=0
            ),
            date_now,
        )
        # create a second manual delivery for next week
        date_next_week = date_now + relativedelta(weeks=1)
        wizard = (
            self.env["manual.delivery"]
            .with_context(
                {
                    "active_model": "sale.order.line",
                    "active_ids": self.so.order_line[1].ids,
                }
            )
            .create(
                {
                    "order_id": self.so.id,
                    "carrier_id": self.so.carrier_id.id,
                    "date_planned": date_next_week,
                }
            )
        )
        wizard.onchange_line_ids()
        for line in wizard.line_ids:
            line.to_ship_qty = 3.0
        wizard.record_picking()
        self.assertEqual(
            len(self.so.picking_ids),
            2,
            "Sale Manual Delivery: second picking should be created after"
            ' "manual delivery" wizard call with different date',
        )
        second_picking = self.so.picking_ids - first_picking
        self.assertEqual(
            datetime.strptime(second_picking.min_date, DF).replace(
                hour=0, minute=0, second=0, microsecond=0
            ),
            date_next_week,
        )
        # create a third manual delivery for today (should be mixed with first)
        new_date_now = datetime.now()
        wizard = (
            self.env["manual.delivery"]
            .with_context(
                {
                    "active_model": "sale.order.line",
                    "active_ids": self.so.order_line[0].ids,
                }
            )
            .create(
                {
                    "order_id": self.so.id,
                    "carrier_id": self.so.carrier_id.id,
                    "date_planned": new_date_now,
                }
            )
        )
        wizard.onchange_line_ids()
        for line in wizard.line_ids:
            line.to_ship_qty = 5.0
        wizard.record_picking()
        self.assertEqual(
            len(self.so.picking_ids),
            2,
            "Sale Manual Delivery: new moves should be merged in first picking"
            ' after "manual delivery" wizard call with same date',
        )
        self.assertEqual(
            sum(first_picking.mapped("move_lines.product_uom_qty")), 7
        )

    def test_04_sale_single_picking(self):
        """
        Test SO's various manual delivery
        """
        self.partner = self.env.ref("base.res_partner_1")
        self.product = self.env.ref("product.product_delivery_01")
        self.product2 = self.env.ref("product.product_delivery_02")
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
                        "product_uom_qty": 1.0,
                        "product_uom": self.product.uom_id.id,
                        "price_unit": self.product.list_price,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": self.product2.name,
                        "product_id": self.product2.id,
                        "product_uom_qty": 2.0,
                        "product_uom": self.product2.uom_id.id,
                        "price_unit": self.product2.list_price,
                    },
                ),
            ],
            "pricelist_id": self.env.ref("product.list0").id,
            "manual_delivery": True,
        }
        self.so1 = self.env["sale.order"].create(so_vals)
        # confirm our standard so, check the picking
        self.so1.action_confirm()
        # create a manual delivery for part of ordered quantity
        wizard = (
            self.env["manual.delivery"]
            .with_context(
                {
                    "active_model": "sale.order.line",
                    "active_ids": self.so1.order_line.ids,
                }
            )
            .create({})
        )
        wizard.onchange_line_ids()
        wiz_act = self.env.ref(
            "sale_manual_delivery.action_wizard_manual_delivery"
        ).read()[0]
        wiz_act["res_id"] = wizard.id
        wiz = self.env[wiz_act["res_model"]].browse(wiz_act["res_id"])
        wiz.record_picking()
        self.assertEqual(
            len(self.so1.picking_ids),
            1.0,
            "Sale Manual \
            Delivery: picking number should be 1.0 instead of %s as created\
            at once"
            % len(self.so1.picking_ids),
        )
