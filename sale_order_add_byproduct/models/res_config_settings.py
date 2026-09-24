# © 2025 OBS Solutions
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    byproduct_note_template = fields.Char(
        related="company_id.byproduct_note_template",
        readonly=False,
    )
