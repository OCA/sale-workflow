# Copyright 2019 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleDeliveryBlockReason(models.Model):
    _name = "sale.delivery.block.reason"
    _description = "Sale Delivery Block Reason"

    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")
    sale_order_ids = fields.One2many(
        comodel_name="sale.order",
        inverse_name="delivery_block_id",
        string="Sale Orders",
        readonly=True,
    )
