# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo.tests import TransactionCase


class TestSaleProductReturnable(TransactionCase):

    def setUp(self):
        super(TestSaleProductReturnable, self).setUp()
        self.tax_model = self.env['account.tax']
        self.SaleOrder = self.env['sale.order']
        self.stock_picking = self.env['stock.picking']

        self.partner_18 = self.env.ref('base.res_partner_18')
        self.pricelist = self.env.ref('product.list0')
        self.product_10 = self.env.ref('product.product_product_10')
        self.product_4d = self.env.ref('product.product_product_4d')
        self.product_uom_unit = self.env.ref('uom.product_uom_unit')

    def test_action_confirm(self):
        self.product_10.returnable = True
        self.product_10.return_product_id = self.product_4d.id

        # Create sale order
        self.percent_tax = self.tax_model.create({
            'name': "Percent tax",
            'amount_type': 'percent',
            'amount': 10,
            'sequence': 3,
        })
        self.sale = self.SaleOrder.create({
            'partner_id': self.partner_18.id,
            'partner_invoice_id': self.partner_18.id,
            'partner_shipping_id': self.partner_18.id,
            'pricelist_id': self.pricelist.id,
            'order_line': [(0, 0, {
                'name': 'PC Assamble + 2GB RAM',
                'product_id': self.product_10.id,
                'product_uom_qty': 1,
                'product_uom': self.product_uom_unit.id,
                'price_unit': 750.00,
                'tax_id': [(4, self.percent_tax.id, 0)]
            })],
        })

        self.sale.action_confirm()
        picking = self.sale.picking_ids.filtered(
            lambda picking: picking.location_dest_id ==
            self.sale.partner_id.property_stock_customer)
        return_picking = self.stock_picking.search(
            [('origin', '=', picking.origin),
             ('id', '!=', picking.id)])
        self.assertTrue(self.sale.state == 'sale')
        same_qty = []
        # compare the quantity of picking and return picking.
        for move in picking.move_line_ids_without_package:
            for return_move in return_picking.move_line_ids_without_package:
                if (move.product_id.returnable and
                        move.product_id.return_product_id.id ==
                        return_move.product_id.id):
                    if (move.product_uom_qty ==
                            return_move.product_uom_qty):
                        same_qty.append(True)
                    else:
                        same_qty.append(False)
        self.assertTrue(all(same_qty), True)
