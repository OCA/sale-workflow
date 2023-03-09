# Copyright 2021 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    sale_line_ids = fields.Many2many(
        comodel_name="sale.order.line",
        relation="sale_line_production_rel",
        column1="production_id",
        column2="line_id",
        string="Sale order line",
    )
