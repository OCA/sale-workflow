# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_workflow_copy_mode = fields.Selection(
        selection=[
            ("no_copy", "Don't copy"),
            ("copy", "Copy"),
        ],
        string="Copy workflow on duplication",
        config_parameter="sale_automatic_workflow.sale_workflow_copy_mode",
        default="no_copy",
        help="Controls whether the automatic workflow is propagated when a sale "
        "order is duplicated (this includes order splits).",
    )
