# Copyright 2019 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    default_delivery_block = fields.Many2one(
        comodel_name="sale.delivery.block.reason",
        string="Default Delivery Block Reason",
        help="Set a reason to block by default the deliveries in this "
        "customer sales orders.",
    )

    @api.model
    def _commercial_fields(self):
        commercial_fields = super()._commercial_fields()
        commercial_fields.append("default_delivery_block")
        return commercial_fields
