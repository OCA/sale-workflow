# -*- coding: utf-8 -*-
# Copyright 2016 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class SaleLayoutCategory(models.Model):
    _inherit = 'sale_layout.category'

    @api.model
    def _default_company_id(self):
        company = self.env['res.company']
        return company.browse(company._company_default_get(
            'sale_layout.category'))

    company_id = fields.Many2one(
        'res.company', string='Company', change_default=True,
        default=_default_company_id)
