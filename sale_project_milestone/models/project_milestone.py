# Copyright 2025 Innovyou
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProjectMilestone(models.Model):
    _inherit = "project.milestone"

    @api.onchange("sale_line_id")
    def _onchange_sale_line_id(self):
        """When linking a sale line, set quantity_percentage to 1 if not set"""
        if self.sale_line_id and not self.quantity_percentage:
            self.quantity_percentage = 1.0
