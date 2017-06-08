# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def name_get(self):
        """Add amount_untaxed in name_get of sale orders"""
        res = super(SaleOrder, self).name_get()
        if self._context.get('sale_order_show_amount'):
            new_res = []
            for (sale_id, name) in res:
                sale = self.browse(sale_id)
                # I didn't find a python method to easily display
                # a float + currency symbol (before or after)
                # depending on lang of context and currency
                name += _(' Amount w/o tax: %s %s)') % (
                    sale.amount_untaxed, sale.currency_id.name)
                new_res.append((sale_id, name))
            return new_res
        else:
            return res
