# -*- coding: utf-8 -*-
# © 2016 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    buy_service_rule_id = fields.Many2one(
        'procurement.rule',
        string='Buy Service Rule')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def need_procurement(self):
        res = super(ProductProduct, self).need_procurement()
        for product in self:
            if not res and product.type == 'service' and \
                    product.buy_service_rule_id:
                return True
        return res
