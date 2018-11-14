# -*- coding: utf-8 -*-
# Copyright 2018 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.osv import fields as old_fields


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    def _get_sale_id(self, cr, uid, ids, name, args, context=None):
        res = {}
        line_model = self.pool['sale.order.line']
        for picking in self.browse(cr, uid, ids, context=context):
            res[picking.id] = super(StockPicking, self)._get_sale_id(
                cr, uid, picking.ids, name, args, context=context)[picking.id]
            if not res[picking.id] and picking.group_id:
                line_id = line_model.search(
                    cr, uid,
                    [('procurement_group_id', '=', picking.group_id.id)],
                    limit=1, context=context)
                line = line_model.browse(cr, uid, line_id, context=context)
                res[picking.id] = line.order_id
        return res

    min_dt = fields.Date(
        string='Scheduled Date (for filter purpose only)',
        compute='_compute_min_dt', store=True)

    _columns = {
        'sale_id': old_fields.function(
            _get_sale_id, type="many2one", relation="sale.order",
            string="Sale Order"),
    }

    @api.multi
    @api.depends('min_date')
    def _compute_min_dt(self):
        for picking in self:
            min_dt = fields.Date.from_string(picking.min_date)
            picking.min_dt = min_dt
