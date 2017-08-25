# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class SaleLayoutCategory(models.Model):
    _inherit = 'sale.layout_category'

    hidden = fields.Boolean(default=False)

    @api.model
    def create(self, values):
        if values.get('hidden'):
            values = values.copy()
            values.update({
                'subtotal': False,
                'pagebreak': False,
            })
        return super(SaleLayoutCategory, self).create(values)

    @api.model
    def write(self, values):
        if values.get('hidden'):
            values = values.copy()
            values.update({
                'subtotal': False,
                'pagebreak': False,
            })
        return super(SaleLayoutCategory, self).write(values)
