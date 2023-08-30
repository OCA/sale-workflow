# Copyright 2021 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tests.common import Form


class ResourceBooking(models.Model):
    _inherit = "resource.booking"

    sale_order_line_id = fields.Many2one(
        "sale.order.line",
        string="Sale order line",
        copy=False,
        index=True,
        ondelete="cascade",
        tracking=True,
    )
    sale_order_line_ids = fields.One2many(
        "sale.order.line",
        "resource_booking_id",
        string="Sale order lines",
    )
    sale_order_id = fields.Many2one(
        related="sale_order_line_id.order_id",
        readonly=True,
        help="Sale order that origins this booking.",
    )
    sale_order_state = fields.Selection(
        string="Sale order state",
        related="sale_order_id.state",
        readonly=True,
        help=(
            "If there is a related quotation and it is not confirmed, "
            "the booking will not be able to become confirmed."
        ),
    )
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        context="{'default_resource_booking_type_id': type_id}",
        domain="[('resource_booking_type_id', '=', type_id)]",
    )

    @api.depends(
        "active", "meeting_id.attendee_ids.state", "sale_order_line_id.order_id.state"
    )
    def _compute_state(self):
        """A booking can only be confirmed if its sale order is confirmed.

        Note: when buying online, the SO is automatically confirmed when paid,
        which makes this actually move the booking from scheduled to confirmed
        automatically after payment.
        """
        result = super()._compute_state()
        # False means "no sale order"
        confirmable_states = {False, "sale", "done"}
        for one in self:
            # Only affect confirmed bookings related to unconfirmed quotations
            if one.state != "confirmed" or one.sale_order_state in confirmable_states:
                continue
            # SO is not confirmed; neither is booking
            one.state = "scheduled"
        return result

    @api.onchange("type_id")
    def _onchange_type_id(self):
        products = self.type_id.product_ids
        if len(products) == 1:
            self.product_id = products

    def action_sale_order_wizard(self):
        """Help user creating a sale order for this RB."""
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "sale_resource_booking.resource_booking_sale_action"
        )
        result["context"] = dict(
            self.env.context,
            default_partner_id=self.partner_id.id,
            default_product_id=self.product_id.id,
            default_type_id=self.type_id.id,
        )
        return result

    def action_generate(self):
        # Based on resource.booking.sale
        self.ensure_one()
        if not self.product_id:
            raise UserError(_("You must select a product to create a sale order."))
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.partner_id
        with so_form.order_line.new() as sol_form:
            sol_form.product_id = self.product_id
        so = so_form.save()  # create sale order and line(s)
        self.sale_order_line_id = so.order_line.filtered(
            lambda l: l.product_id == self.product_id
        ).id
        return {
            "res_id": so.id,
            "res_model": "sale.order",
            "target": "current",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "views": [[False, "form"]],
        }
