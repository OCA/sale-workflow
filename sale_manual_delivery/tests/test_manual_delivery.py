# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields
from odoo.addons.sale.tests.test_sale_common import TestSale
from datetime import datetime
from dateutil.relativedelta import relativedelta


class TestSaleStock(TestSale):

    def setUp(self):
        super().setUp()
        self.partner = self.env.ref('base.res_partner_1')
        self.product = self.env.ref('product.product_delivery_01')
        self.stock_location = self.env.ref('stock.stock_location_stock')
        self.env['stock.quant']._update_available_quantity(
            self.product, self.stock_location, 100)

    def test_00_sale_manual_delivery(self):
        """
        Test SO's manual delivery
        """
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
        for line in wizard.line_ids:
            line.to_ship_qty = line.ordered_qty
        wizard.record_picking()
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
        self.assertFalse(
            wizard.line_ids,
            "Sale Manual Delivery: After picking \
            creation for all products, no lines should be left in the wizard",
        )

        wizard.record_picking()
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
        pick.move_line_ids.write({"qty_done": 5})
        pick.button_validate()

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
        pick.move_line_ids.write({"qty_done": 5})
        pick.button_validate()

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
        for line in wizard.line_ids:
            line.to_ship_qty = 2.0
        wizard.record_picking()
        # check picking is created
        self.assertTrue(
            self.so.picking_ids,
            'Sale Manual Delivery: picking \
            should be created after "manual delivery" wizard call',
        )

        # deliver completely
        pick = self.so.picking_ids
        pick.action_assign()
        pick.move_line_ids.write({"qty_done": 2})
        pick.button_validate()

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
        for line in wizard.line_ids:
            line.to_ship_qty = 3.0
        wizard.record_picking()
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

    def test_03_sale_multi_delivery(self):
        self.product_2 = self.env.ref('product.product_delivery_02')
        self.env['stock.quant']._update_available_quantity(
            self.product_2, self.stock_location, 100)
        so_vals = {
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'order_line': [
                (0, 0, {
                    'name': self.product.name,
                    'product_id': self.product.id,
                    'product_uom_qty': 10.0,
                    'product_uom': self.product.uom_id.id,
                    'price_unit': self.product.list_price
                }), (0, 0, {
                    'name': self.product_2.name,
                    'product_id': self.product_2.id,
                    'product_uom_qty': 10.0,
                    'product_uom': self.product_2.uom_id.id,
                    'price_unit': self.product_2.list_price
                })
            ],
            'pricelist_id': self.env.ref('product.list0').id,
            'manual_delivery': True,
        }
        self.so = self.env['sale.order'].create(so_vals)

        # confirm our standard so, check the picking
        self.so.action_confirm()
        self.assertFalse(self.so.picking_ids, 'Sale Manual Delivery: no \
            picking should be created for "manual delivery" orders')
        # create a manual delivery for part of ordered quantity
        date_now = datetime.now()
        wizard = self.env['manual.delivery'].create({
            'order_id': self.so.id,
            'carrier_id': self.so.carrier_id.id,
            'date_planned': date_now,
        })
        wizard.onchange_order_id()
        for line in wizard.line_ids:
            line.to_ship_qty = 2.0
        wizard.record_picking()
        # check picking is created
        self.assertEqual(
            len(self.so.picking_ids),
            1,
            'Sale Manual Delivery: picking should be created after "manual'
            ' delivery" wizard call'
        )
        first_picking = self.so.picking_ids
        self.assertEqual(
            first_picking.scheduled_date, fields.Datetime.to_string(date_now)
        )
        # create a second manual delivery for next week
        date_next_week = date_now + relativedelta(weeks=1)
        wizard = self.env['manual.delivery'].create({
            'order_id': self.so.id,
            'carrier_id': self.so.carrier_id.id,
            'date_planned': date_next_week,
        })
        wizard.onchange_order_id()
        for line in wizard.line_ids:
            line.to_ship_qty = 3.0
        wizard.record_picking()
        self.assertEqual(
            len(self.so.picking_ids),
            2,
            'Sale Manual Delivery: second picking should be created after'
            ' "manual delivery" wizard call with different date'
        )
        second_picking = self.so.picking_ids - first_picking
        self.assertEqual(
            second_picking.scheduled_date,
            fields.Datetime.to_string(date_next_week)
        )
        # create a third manual delivery for today (should be mixed with first)
        new_date_now = datetime.now()
        wizard = self.env['manual.delivery'].create({
            'order_id': self.so.id,
            'carrier_id': self.so.carrier_id.id,
            'date_planned': new_date_now,
        })
        wizard.onchange_order_id()
        for line in wizard.line_ids:
            line.to_ship_qty = 5.0
        wizard.record_picking()
        self.assertEqual(
            len(self.so.picking_ids),
            2,
            'Sale Manual Delivery: new moves should be merged in first picking'
            ' after "manual delivery" wizard call with same date'

        )
        for move in first_picking.move_lines:
            self.assertEqual(move.product_uom_qty, 7)
