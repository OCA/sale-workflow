# -*- coding: utf-8 -*-
# Copyright 2016 Andrea Cometa - Apulia Software
# License AGPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def total_weight(self):
        """
        Returns total weight from a specified sale order
        """
        lines = self.order_line
        total_weight = 0.0
        for line in lines:
            if line.product_id:
                total_weight += (
                    line.product_id.weight * line.product_uom_qty)
        return total_weight
