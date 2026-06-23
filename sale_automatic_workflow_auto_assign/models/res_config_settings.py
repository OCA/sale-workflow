# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_workflow_copy_mode = fields.Selection(
        selection_add=[("copy_fallback", "Copy if auto-assign finds none")],
        ondelete={"copy_fallback": "set default"},
        help="Controls whether the automatic workflow is propagated when a sale "
        "order is duplicated (this includes order splits):\n"
        "- Don't copy: the workflow is re-derived from the auto-assign rules only.\n"
        "- Copy: the origin workflow is always copied, auto-assign is not re-run.\n"
        "- Copy if auto-assign finds none: auto-assign runs first; the origin "
        "workflow is copied only when no workflow could be auto-assigned.",
    )
