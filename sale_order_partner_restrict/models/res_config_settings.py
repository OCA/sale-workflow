# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_order_partner_restrict = fields.Selection(
        related="company_id.sale_order_partner_restrict",
        string="Partner Restriction on Sale Orders",
        readonly=False,
    )
