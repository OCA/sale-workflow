# Copyright 2020 Tecnativa - Sergio Teruel

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    default_sale_recommendation_price_origin = fields.Selection(
        [("pricelist", "Pricelist"), ("last_sale_price", "Last sale price")],
        string="Price origin",
        default="pricelist",
        default_model="sale.order.recommendation",
        required=True,
    )

    default_use_delivery_address = fields.Boolean(
        string="Use delivery address", default_model="sale.order.recommendation"
    )
    default_months = fields.Float(
        string="Default sale recommendation months",
        default_model="sale.order.recommendation",
        default=6,
    )
    default_line_amount = fields.Integer(
        string="Default sale number of recommendations",
        default_model="sale.order.recommendation",
        default=15,
    )
    force_zero_units_included = fields.Boolean(
        related="company_id.force_zero_units_included",
        readonly=False,
        help="Add recomented products in so even if units included is zero.",
    )
    sale_line_recommendation_domain = fields.Char(
        related="company_id.sale_line_recommendation_domain",
        readonly=False,
        help="Domain applied to find SO lines to propose as recommended products.",
    )
