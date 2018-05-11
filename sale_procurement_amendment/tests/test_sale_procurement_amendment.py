# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestSaleProcurementAmendment(common.TransactionCase):

    def setUp(self):
        super(TestSaleProcurementAmendment, self).setUp()
        self.sale_obj = self.env['sale.order']
        self.sale_order_line_obj = self.env['sale.order.line']
        self.product1 = self.env.ref('product.product_product_12')
        self.agrolait = self.env.ref('base.res_partner_2')

    def _create_sale_order(self):

        vals = {
            'partner_id': self.agrolait.id,
        }
        self.order = self.sale_obj.create(vals)
        self.order.onchange_partner_id()
        vals = {
            'order_id': self.order.id,
            'product_id': self.product1.id,
            'product_uom_qty': 10.0,
        }
        self.sale_line = self.sale_order_line_obj.create(vals)
        self.sale_line.product_id_change()

    def test_00_pickings_in_progress(self):
        """
        Test the picking_in_progress and can_be_amended values
        :return:
        """
        self._create_sale_order()
        self.order.action_confirm()
        self.assertEquals(
            1,
            len(self.order.picking_ids),
        )
        self.assertTrue(
            self.order.picking_ids.move_lines.can_be_amended,
        )
        self.assertFalse(
            self.sale_line.pickings_in_progress,
        )

    def test_01_pickings_in_progress_op(self):
        """
        Test the picking_in_progress and can_be_amended values
        Pack operations are in progress
        :return:
        """
        self._create_sale_order()
        self.order.action_confirm()

        self.order.picking_ids.pack_operation_ids.qty_done = 1.0
        self.assertFalse(
            self.order.picking_ids.move_lines.can_be_amended,
        )
        self.assertTrue(
            self.sale_line.pickings_in_progress,
        )

    def test_02_pickings_in_progress_backorder(self):
        """
        Test the picking_in_progress and can_be_amended values
        A picking was done and a backorder is created
        :return:
        """
        self._create_sale_order()
        self.order.action_confirm()
        self.order.picking_ids.action_assign()
        self.order.picking_ids.pack_operation_ids.qty_done = 1.0
        wizard = self.env['stock.backorder.confirmation'].create({
            'pick_id': self.order.picking_ids.id,
        })
        wizard.process()
        # self.order.picking_ids.do_transfer()
        self.assertEquals(
            [True, False],
            self.order.picking_ids.mapped('move_lines.can_be_amended'),
        )
        self.assertTrue(
            self.sale_line.pickings_in_progress,
        )

    def test_03_decrease_sale_line(self):
        """
        Decrease Sale Order Line
        :return:
        """
        self._create_sale_order()
        self.order.action_confirm()
        move_out = self.order.picking_ids.move_lines.filtered(
            lambda m: m.picking_id.location_dest_id.usage == 'customer')
        self.assertEquals(
            10.0,
            move_out.product_uom_qty
        )
        # Decrease qty
        self.sale_line.write({'product_uom_qty': 9.0})
        self.assertEquals(
            'cancel',
            move_out.state,
        )

        move_out = self.order.picking_ids.mapped('move_lines').filtered(
            lambda m: m.state != 'cancel' and
            m.picking_id.location_dest_id.usage == 'customer')
        self.assertEquals(
            9.0,
            move_out.product_uom_qty,
        )
