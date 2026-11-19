# Copyright 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2013 Camptocamp SA (author: Guewen Baconnier)
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleWorkflowProcess(models.Model):
    """Extend to add stock related workflow process."""

    _inherit = "sale.workflow.process"

    picking_policy = fields.Selection(
        selection=[
            ("direct", "Deliver each product when available"),
            ("one", "Deliver all products at once"),
        ],
        string="Shipping Policy",
        default="direct",
    )
    validate_picking = fields.Boolean(string="Confirm and Transfer Picking")
    picking_filter_domain = fields.Text(
        string="Picking Filter Domain", related="picking_filter_id.domain"
    )
    picking_filter_id = fields.Many2one(
        "ir.filters",
        string="Picking Filter",
        default=lambda self: self._default_filter(
            "sale_automatic_workflow_stock.automatic_workflow_picking_filter"
        ),
    )
