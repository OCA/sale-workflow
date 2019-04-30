# -*- coding: utf-8 -*-
# © 2014 Today Akretion (http://www.akretion.com).
#  @author Adrien CHAUSSENDE <adrien.chaussende@akretion.com>
# @author  Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from .common import TestMrpLotCommon


class BaseTest(TestMrpLotCommon):
    def setUp(self):
        super(BaseTest, self).setUp()
        self.product_obj = self.env['product.product']
        self.sale_order_obj = self.env['sale.order']
        self.order_line_obj = self.env['sale.order.line']
        self.partner_obj = self.env['res.partner']
        self.move_obj = self.env['stock.move']
        self.order_line_obj = self.env['sale.order.line']
        self.mrp_prod_obj = self.env['mrp.production']
        self.bom_obj = self.env['mrp.bom']
        self.prodlot_obj = self.env['stock.production.lot']

        self.partner = self.partner_obj.search(
            [('customer', '=', 'True')])[0]

    def _init_sale_order(self):
        """
            Create a sale order based on list of product ids that are contained
            in self. Uses _init_product_ids and _init_partner_id.
        """
        # Create sale order_infos_keys
        sale_order_vals = {
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'pricelist_id': self.env.ref('product.list0').id,
        }
        self.sale_order = self.sale_order_obj.create(sale_order_vals)

        # Sale order lines
        order_line = {
            'order_id': self.sale_order.id,
            'name': self.product_3.name,
            'product_id': self.product_3.id,
            'product_uom_qty': 5,
            'product_uom': self.product_3.uom_id.id,
            'price_unit': self.product_3.list_price,
        }
        self.order_line_obj.create(order_line)
        self.sale_order.action_confirm()

    def _search_procurements(self):
        # stock_location = self.env.ref('stock.stock_location_stock')
        return self.env['procurement.order'].search(
            [('group_id.name', 'ilike', self.sale_order.name)])


class TestSuccess(BaseTest):
    def setUp(self):
        super(TestSuccess, self).setUp()
        self._init_sale_order()

    def test_00_mo_create(self):
        """ Check if the create function is setting a move-to-production id
            and a production lot id
        """
        order_line = self.sale_order.order_line[0]
        lot_name = order_line.lot_id.name
        procs = self._search_procurements()
        production_name = False
        for proc in procs:
            proc.run()
            production_name = proc.production_id.name
            if proc.product_id.id in [
                    bom_l.id for bom_l in self.bom_1.bom_line_ids]:
                sub_lot_number = "%s-%01d" % (lot_name, 1)
                self.assertEquals(
                    production_name, sub_lot_number,
                    "Incorrect name for Manufacturing Order,"
                    " should be '%s'" % (
                        sub_lot_number))
