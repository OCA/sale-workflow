# Copyright 2019 ForgeFlow S.L.
#   (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleDeliveryBlockReason(models.Model):
    _name = "sale.delivery.block.reason"
    _description = "Sale Delivery Block Reason"

    name = fields.Char(required=True)
    description = fields.Text()
    sale_order_ids = fields.One2many(
        comodel_name="sale.order",
        inverse_name="delivery_block_id",
        string="Sale Orders",
        readonly=True,
    )
