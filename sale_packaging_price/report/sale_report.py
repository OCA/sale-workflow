# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class SaleReport(models.Model):
    _inherit = 'sale.report'

    product_packaging = fields.Many2one(
        comodel_name='product.packaging', string='Product Package',
        readonly=True)
    qty_packaging = fields.Integer(string='Qty Package', readonly=True)

    def _select(self):
        res = super(SaleReport, self)._select()
        return res + ', l.product_packaging as product_packaging' \
                     ', sum(l.product_uom_qty / pk.qty) as qty_packaging'

    def _from(self):
        res = super(SaleReport, self)._from()
        return res + ' left join product_packaging pk on (' \
                     'pk.id = l.product_packaging)'

    def _group_by(self):
        res = super(SaleReport, self)._group_by()
        return res + ', l.product_packaging'
