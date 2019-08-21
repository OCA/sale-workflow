# Copyright 2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from odoo.tools import float_compare
from odoo.exceptions import UserError
from odoo.tools.translate import _


class ManualDelivery(models.TransientModel):
    """Creates procurements manually"""

    _name = "manual.delivery"
    _order = "create_date desc"

    def _set_order_id(self):
        return self.env["sale.order"].browse(self._context["active_ids"])

    @api.onchange("order_id")
    def onchange_order_id(self):
        lines = []
        if self.order_id:
            for line in self.order_id.order_line:
                if (
                    not line.existing_qty == line.product_uom_qty
                    and line.product_id.type != "service"
                ):
                    vals = {
                        "order_line_id": line.id,
                        "ordered_qty": line.product_uom_qty,
                        "existing_qty": line.existing_qty,
                    }
                    lines.append((0, 0, vals))
            self.update({"line_ids": lines})

            self.partner_id = self.order_id.partner_id

    date_planned = fields.Datetime(string="Date Planned")
    order_id = fields.Many2one(
        "sale.order", string="Sale Order", default=_set_order_id  # TODO HIDE
    )
    line_ids = fields.One2many(
        "manual.delivery.line",
        "manual_delivery_id",
        string="Lines to validate"
    )
    carrier_id = fields.Many2one("delivery.carrier", string="Delivery Method")
    partner_id = fields.Many2one("res.partner", string="Delivery Address")

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        return {
            "domain": {
                "partner_id": [
                    "&",
                    "|",
                    ("id", "=", self.order_id.partner_id.id),
                    ("parent_id", "=", self.order_id.partner_id.id),
                    ("id", "!=", self.partner_id.id),
                ]
            }
        }

    @api.multi
    def record_picking(self):
        proc_group_obj = self.env["procurement.group"]
        for wizard in self:
            carrier_id = wizard.carrier_id if wizard.carrier_id \
                else wizard.order_id.carrier_id
            date_planned = wizard.date_planned
            order = wizard.order_id
            if not order.procurement_group_id:
                vals = {
                    "name": order.name,
                    "move_type": order.picking_policy,
                    "sale_id": order.id,
                    "partner_id": order.partner_shipping_id.id,
                }
                order.procurement_group_id = proc_group_obj.create(vals)

            for line in wizard.line_ids:
                if line.to_ship_qty > line.ordered_qty - line.existing_qty:
                    raise UserError(
                        _(
                            "You can not deliver more than the "
                            "remaining quantity. If you need to do "
                            "so, please edit the sale order first."
                        )
                    )
                if float_compare(line.to_ship_qty, 0, 2):
                    vals = line.order_line_id._prepare_procurement_values(
                        group_id=order.procurement_group_id
                    )
                    vals["date_planned"] = date_planned
                    vals["carrier_id"] = carrier_id.id
                    vals["partner_dest_id"] = wizard.partner_id.id
                    so_id = line.order_line_id.order_id
                    proc_group_obj.run(
                        line.order_line_id.product_id,
                        line.to_ship_qty,
                        line.order_line_id.product_uom,
                        so_id.partner_shipping_id.property_stock_customer,
                        line.order_line_id.name,
                        so_id.name,
                        vals,
                    )
