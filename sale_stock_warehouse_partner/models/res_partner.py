# Copyright 2025 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        company_dependent=True,
        string="Warehouse",
        help="Set default warehouse for Sale Order",
    )
