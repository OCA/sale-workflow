# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # Store the section link so domains and section-based analysis can use it
    # directly without reconstructing the relation from line sequence. Since
    # the field is expected to be used in searches and filters, indexing it is
    # justified.
    section_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Section",
        compute="_compute_section_id",
        compute_sudo=True,
        store=True,
        index=True,
    )

    @api.depends(
        "order_id",
        "display_type",
        "order_id.order_line",
        "order_id.order_line.sequence",
        "order_id.order_line.display_type",
        "sequence",
    )
    def _compute_section_id(self):
        for line in self:
            order = line.order_id
            if not order or line.display_type == "line_section":
                line.section_id = False
                continue

            current_section = False
            for order_line in order.order_line.sorted("sequence"):
                if order_line == line:
                    break
                if order_line.display_type == "line_section":
                    current_section = order_line
            line.section_id = current_section
