# Copyright 2024 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    default_delivery_block_reason_id = fields.Many2one(
        comodel_name="sale.delivery.block.reason",
        string="Default Delivery Block Reason",
        help="Set a reason to block by default the deliveries in this "
        "payment term sales orders.",
    )
