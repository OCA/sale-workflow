# -*- coding: utf-8 -*-
#
#
#    Author: Guewen Baconnier
#    Copyright 2013 Camptocamp SA
#    Copyright 2016 Serpent Consulting Services Pvt. Ltd.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from openerp.tests.common import TransactionCase


class SaleOrderTestCase(TransactionCase):
    def setup(self):
        super(SaleOrderTestCase, self).setup()

    def test_saleorder_action(self):
        self.cancel_reason = self.env['sale.order.cancel.reason']
        self.reason_id = self.cancel_reason.create({
            'name': 'Test Sale Order Cancel Reason',
            'active': True,
        })

        self.sale_order_cancel = self.env['sale.order.cancel']
        self.sale_order_cancel_id = self.sale_order_cancel.create({
            'reason_id': self.reason_id.id,
        })

        self.sale_order = self.env['sale.order']
        self.partner = self.env.ref('base.res_partner_1')
        self.order_id = self.sale_order.create({
            'partner_id': self.partner.id,
        })
        self.sale_order_cancel_id.with_context({
            'active_ids': [self.order_id.id]
        }).confirm_cancel()

        self.products = {
            'prod_order': self.env.ref('product.product_product_43'),
            'prod_del': self.env.ref('product.product_product_47'),
            'serv_order': self.env.ref('product.product_product_0'),
            'serv_del': self.env.ref('product.product_product_56'),
        }

        self.order_idA = self.sale_order.create({
            'partner_id': self.partner.id,
            'state': 'sale',
            'order_line': [
                (0, 0, {'name': p.name, 'product_id': p.id,
                        'product_uom_qty': 2, 'product_uom': p.uom_id.id,
                        'price_unit': p.list_price,
                        })for (_, p) in self.products.iteritems()],
            })

        self.sale_order_cancel_idA = self.sale_order_cancel.create({
            'reason_id': self.reason_id.id,
        })

        self.sale_order_cancel_idA.with_context({
            'active_ids': [self.order_idA.id]
        }).confirm_cancel()
