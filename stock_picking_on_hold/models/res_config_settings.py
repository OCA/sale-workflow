# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    hold_picking_until_payment = fields.Boolean(
        help="Hold deliveries on sale orders without a payment method until invoiced",
        config_parameter="stock_picking_on_hold.hold_picking_until_payment",
        default=True,
    )
