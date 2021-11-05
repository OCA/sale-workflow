# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tests.common import Form


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
        "res.partner", string="Customer", index=True, ondelete="cascade", required=True
    )
    product_id = fields.Many2one(
        "product.product",
        "Product",
        context="{'default_resource_booking_type_id': type_id}",
        domain="[('resource_booking_type_id', '=', type_id)]",
        index=True,
        ondelete="cascade",
        required=True,
    )
    product_uom_qty = fields.Integer(string="Quantity", required=True, default=1)

    def action_generate(self):
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.partner_id
        with so_form.order_line.new() as sol_form:
            sol_form.product_id = self.product_id
            sol_form.product_uom_qty = self.product_uom_qty
        so = so_form.save()
        return {
            "res_id": so.id,
            "res_model": "sale.order",
            "target": "current",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "views": [[False, "form"]],
        }
