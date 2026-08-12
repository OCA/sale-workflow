# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, fields, models


class ResourceBookingSale(models.TransientModel):
    _name = "resource.booking.sale"
    _description = "Sale order generator for resource booking types"

    type_id = fields.Many2one(
        "resource.booking.type",
        string="Booking type",
        index=True,
        ondelete="cascade",
        required=True,
    )
    partner_id = fields.Many2one(
        "res.partner", string="Customer", ondelete="cascade", required=True
    )
    product_id = fields.Many2one(
        "product.product",
        "Product",
        domain="[('resource_booking_type_id', '=', type_id)]",
        ondelete="cascade",
        required=True,
    )
    product_uom_qty = fields.Integer(string="Quantity", required=True, default=1)

    def action_generate(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner_id.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_id.id,
                            "product_uom_qty": self.product_uom_qty,
                        }
                    )
                ],
            }
        )
        return order._get_records_action()
