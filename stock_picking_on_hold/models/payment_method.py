# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PaymentMethod(models.Model):
    _inherit = "account.payment.method"

    hold_picking_until_payment = fields.Boolean(
        help="If set to true, pickings will not be automatically confirmed when "
        "the invoice has not been paid.",
    )
