# -*- coding: utf-8 -*-
# Copyright 2015 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    main_exception_id = fields.Many2one(
        'sale.exception',
        compute='_get_main_error',
        string='Main Exception',
        store=True)
    exception_ids = fields.Many2many(
        'sale.exception',
        string='Exceptions')

    @api.multi
    @api.depends('exception_ids')
    def _get_main_error(self):
        for line in self:
            exceptions = line.exception_ids
            line.main_exception_id = exceptions and exceptions or False
