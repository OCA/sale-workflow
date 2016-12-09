# -*- coding: utf-8 -*-
# © 2016  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import openerp.tests.common as common


class TestSaleChangePrice(common.TransactionCase):

    def test_change_price(self):
        """ Create and confirm a sale order
            Change price of a line
            Check new price is set
        """
        product_1 = self.env.ref("product.product_product_35")
        product_2 = self.env.ref("product.product_product_36")
        so = self.env["sale.order"].create(
            {"partner_id": self.env.ref("base.res_partner_2").id})
        sol1 = self.env['sale.order.line'].create(
            {'order_id': so.id,
             'price_unit': 5,
             'product_id': product_1.id})
        sol2 = self.env['sale.order.line'].create(
            {'order_id': so.id,
             'price_unit': 8,
             'product_id': product_2.id})
        so.action_button_confirm()
        self.assertEquals(13, so.amount_total)

        sale_change_price_obj = self.env["sale.change.price"]
        scp = sale_change_price_obj.with_context(
            active_ids=[so.id], active_model='sale.order').create({})

        self.assertEquals(len(scp.item_ids), 2)
        sol1_ok = sol2_ok = False
        for scp_item in scp.item_ids:
            if scp_item.sale_order_line_id.id == sol1.id:
                sol1_ok = True
                scp_item.price_unit = 10
            elif scp_item.sale_order_line_id.id == sol2.id:
                sol2_ok = True
        self.assertTrue(sol1_ok)
        self.assertTrue(sol2_ok)

        scp.change_price()

        self.assertEquals(18, so.amount_total)
