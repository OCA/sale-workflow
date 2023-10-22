# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    hold_picking_until_payment = fields.Boolean(
        help="Hold deliveries on sale orders without a payment method until invoiced",
        default=True,
    )
