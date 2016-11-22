# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
##############################################################################

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sale_type_id = fields.Many2one(
        comodel_name='sale.order.type', string='Sale Order Type')
