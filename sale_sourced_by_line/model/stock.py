# -*- coding: utf-8 -*-
# Copyright 2013-2014 Camptocamp SA - Yannick Vaucher
# © 2015 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
'''
Redefine and override all sale_stock picking method to search procurement
group on sale order line instead of on the sale order
'''
from openerp import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.depends('group_id')
    def _compute_get_sale_id(self):
        sale_line_obj = self.env['sale.order.line']
        for picking in self:
            if picking.group_id:
                lines = sale_line_obj.search(
                    [('procurement_group_id', '=', picking.group_id.id)])
                if lines:
                    self.sale_id = lines[0].order_id

    sale_id = fields.Many2one('sale.order', compute='_compute_get_sale_id',
                              string="Sale Order")
