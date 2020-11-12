# Copyright 2020 Tecnativa - Sergio Teruel

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    default_sale_recommendation_price_origin = fields.Selection([
        ('pricelist', 'Pricelist'),
        ('last_sale_price', 'Last sale price')
        ],
        string="Price origin",
        default='pricelist',
        default_model="sale.order.recommendation",
        required=True
    )
