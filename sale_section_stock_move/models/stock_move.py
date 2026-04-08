# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    sale_section_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Sale Section",
        related="sale_line_id.section_id",
        store=True,
        readonly=True,
        index="btree_not_null",
    )
    sale_section_name = fields.Text(
        string="Section Name",
        related="sale_section_id.name",
        store=True,
        readonly=True,
    )
