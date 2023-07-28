# Copyright 2023 Raumschmiede GmbH
from odoo import fields, models


class Route(models.Model):
    _inherit = "stock.location.route"

    no_sale_stock_prebook = fields.Boolean(
        string="No Sale Stock Prebook",
        help="If set no stock will be prebooked, "
        "for configured Products with this route",
    )
