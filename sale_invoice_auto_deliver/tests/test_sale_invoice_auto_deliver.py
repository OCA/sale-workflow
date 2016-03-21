# -*- coding: utf-8 -*-
# © 2016  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import openerp.tests.common as common


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
             'product_id': self.env.ref("product.product_product_35").id})
        so.action_button_confirm()
        adv_wizard = self.env['sale.advance.payment.inv'].create(
            {'advance_payment_method': 'all_auto'})
        adv_wizard.with_context(active_ids=[so.id]).create_invoices()
        self.assertEquals(so.picking_ids.state, 'done')

    def test_sale_invoice_line_auto_deliver(self):
        """ Create SO
            Create invoice
            Validate invoice + Auto Deliver
            Check picking are done
        """
        so = self.env["sale.order"].create(
            {"partner_id": self.env.ref("base.res_partner_2").id})
        sol = self.env['sale.order.line'].create(
            {'order_id': so.id,
             'product_id': self.env.ref("product.product_product_35").id})
        so.action_button_confirm()
        so.picking_ids.force_assign()
        adv_wizard = self.env['sale.order.line.make.invoice'].create({})
        adv_wizard.with_context(active_ids=[sol.id],
                                auto_deliver=True).make_invoices()
        self.assertEquals(so.picking_ids.state, 'done')
