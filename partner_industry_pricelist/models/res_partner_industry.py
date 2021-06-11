# Copyright 2021 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class ResPartnerIndustry(models.Model):

    _inherit = 'res.partner.industry'

    pricelist_id = fields.Many2one(
        string='Pricelist',
        comodel_name='product.pricelist',
    )
