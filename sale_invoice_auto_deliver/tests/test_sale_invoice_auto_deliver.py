# -*- coding: utf-8 -*-
# © 2016  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import odoo.tests.common as common
from odoo import exceptions


class TestSaleInvoiceAutoDeliver(common.TransactionCase):

    def test_sale_invoice_auto_deliver(self):
        """ Create SO
            Create invoice
            Validate invoice + Auto Deliver
            Check picking are done
        """
        so = self.env["sale.order"].create(
            {"partner_id": self.env.ref("base.res_partner_2").id})
        self.env['sale.order.line'].create(
            {'order_id': so.id,
             'product_id': self.env.ref("product.product_product_9").id})
        so.action_confirm()
        adv_wizard = self.env['sale.advance.payment.inv'].create(
            {'advance_payment_method': 'all_auto'})
        adv_wizard.with_context(active_ids=[so.id]).create_invoices()
        self.assertEquals(so.picking_ids.state, 'done')

    def test_sale_invoice_auto_deliver_no_availability(self):
        """ Create SO on product without stock
            Create invoice
            Validate invoice + Auto Deliver
            Check exception raises
        """
        product_id = self.env.ref("product.product_product_11")
        location_id = self.env['stock.location'].search(
            [('name', '=', 'Shelf 1')])
        inventory = self.env['stock.inventory'].create({
            'name': 'Inventory For Product C',
            'filter': 'partial',
            'line_ids': [(0, 0, {
                'product_id': product_id.id,
                'product_uom_id': product_id.uom_id.id,
                'product_qty': 0,
                'location_id': location_id.id,
            })]
        })
        inventory.action_done()
        so = self.env["sale.order"].create(
            {"partner_id": self.env.ref("base.res_partner_2").id})
        self.env['sale.order.line'].create(
            {'order_id': so.id,
             'product_id': product_id.id})
        so.action_confirm()
        adv_wizard = self.env['sale.advance.payment.inv'].create(
            {'advance_payment_method': 'all_auto'})
        with self.assertRaises(exceptions.Warning):
            adv_wizard.with_context(active_ids=[so.id]).create_invoices()
        self.assertEquals(so.picking_ids.state, 'confirmed')
        for pick in so.picking_ids:
            pack_ops = pick.pack_operation_pack_ids
            self.assertTrue(all(pack_op.qty_done == pack_op.qty for pack_op
                                in pack_ops))
