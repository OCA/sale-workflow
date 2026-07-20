# Copyright 2024 Akretion (http://www.akretion.com/)
# @author: Olivier Nibart <olivier.nibart@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleWorkflowProcess(models.Model):
    _inherit = "sale.workflow.process"

    sale_line_route_id = fields.Many2one(
        "stock.location.route",
        string="Route",
        domain=[("sale_selectable", "=", True)],
        ondelete="restrict",
        check_company=True,
    )

    sale_line_route_policy = fields.Selection(
        [
            ("replace", "Replace: Set route from workflow if defined"),
            ("fill_empty", "Fill Empty: Set route only if line has no route"),
        ],
        string="Route Policy",
        default="replace",
        required=True,
        help="Replace: Always apply workflow route when one is defined.\n"
        "Fill Empty: Only set workflow route on lines that don't already have a route defined.",
    )
