# -*- coding: utf-8 -*-
# © 2016 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _prepare_order_line_procurement(self, order, line, group_id=False):
        res = super(SaleOrder, self)._prepare_order_line_procurement(
            order, line, group_id=group_id)
        if (line.product_id.type == 'service' and
                line.product_id.buy_service_rule_id):
            res['rule_id'] = line.product_id.buy_service_rule_id.id
        return res
