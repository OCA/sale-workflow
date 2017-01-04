# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sale_type = fields.Many2one(
        comodel_name='sale.order.type', string='Sale Order Type',
        company_dependent=True)
