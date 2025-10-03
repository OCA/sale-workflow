# Copyright 2016 Opener B.V. - Stefan Rijnhart
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import Command, _, api, fields, models


class SaleOrderMerge(models.TransientModel):
    _name = "sale.order.merge"
    _description = "Merge sale orders"

    order_id = fields.Many2one(
        "sale.order", "Merge into", required=True, domain="[('id','in',to_merge)]"
    )
    mergeable = fields.Many2many(
        comodel_name="sale.order", related="order_id.merge_with"
    )
    to_merge = fields.Many2many(
        "sale.order",
        "rel_sale_to_merge",
        "sale_id",
        "to_merge_id",
        "Orders to merge",
        domain="[('id','in',mergeable)]",
    )
    message_alert = fields.Boolean(compute="_compute_message_alert", store=True)

    @api.depends("order_id", "to_merge")
    def _compute_message_alert(self):
        for wizard in self:
            wizard.message_alert = wizard.order_id.state == "draft" and any(
                order.state == "sale" for order in wizard.to_merge
            )

    def merge_order_lines(self):
        self.order_id.write(
            {
                "order_line": [
                    Command.link(line.id) for line in self.to_merge.mapped("order_line")
                ]
            }
        )

    def merge_moves(self):
        """Merge all draft invoices. For prepaid orders, the payment
        of the original invoice is leading to start the procurement, but
        there may still be other confirmed invoices."""
        target = self.env["account.move"]
        other_move = self.env["account.move"]
        keep_move = self.env["account.move"]
        invoice_ids = (self.to_merge - self.order_id).mapped("invoice_ids")
        for invoice in invoice_ids:
            if invoice.state == "draft":
                if target:
                    other_move += invoice
                else:
                    target = invoice
            else:
                keep_move += invoice
        if target:
            other_move.mapped("invoice_line_ids").write({"move_id": target.id})
            other_move.unlink()
            target._compute_amount()

        for inv in target | keep_move:
            self.order_id.write({"invoice_ids": [Command.link(inv.id)]})
        self.to_merge.write({"invoice_ids": [Command.set([])]})

    def _picking_can_merge(self, picking):
        return (
            picking.state not in ("done", "cancel")
            and picking.location_dest_id.usage == "customer"
        )

    def _get_picking_map_key(self, picking):
        return (
            picking.picking_type_id,
            picking.location_id,
            picking.location_dest_id,
            picking.partner_id,
        )

    def merge_pickings(self):
        """Assign all pickings to the target sale order and merge any
        pending pickings"""
        orders = self.to_merge - self.order_id
        if self.order_id.procurement_group_id:
            group = self.order_id.procurement_group_id
        else:
            for order in orders:
                if order.procurement_group_id:
                    group = order.procurement_group_id
                    break
            else:
                # no group, no pickings
                return False
            self.order_id.write({"procurement_group_id": group.id})
        other_groups = orders.mapped("procurement_group_id")
        self.env["stock.picking"].search([("group_id", "in", other_groups.ids)]).write(
            {"group_id": group.id}
        )
        self.env["stock.move"].search([("group_id", "in", other_groups.ids)]).write(
            {"group_id": group.id}
        )
        pick_map = {}
        self.to_merge.picking_ids.write(
            {
                "sale_id": self.order_id.id,
                "origin": self.order_id.name,
            }
        )
        for picking in self.order_id.picking_ids:
            if self._picking_can_merge(picking):
                key = self._get_picking_map_key(picking)
                if key not in pick_map:
                    pick_map[key] = self.env["stock.picking"]
                pick_map[key] += picking
            else:
                picking.write({"origin": group.name})
        for pickings in pick_map.values():
            target = pickings[0]
            if len(pickings) > 1:
                pickings -= target
                pickings.mapped("move_line_ids").write({"picking_id": target.id})
            target.write({"origin": group.name})
        return True

    def open_sale(self):
        self.ensure_one()
        return {
            "name": _("Merged sale order"),
            "view_type": "form",
            "view_mode": "form",
            "res_id": self.order_id.id,
            "res_model": "sale.order",
            "type": "ir.actions.act_window",
        }

    def _confirm_orders_by_order_target(self, orders):
        """
        This method allows you to confirm sales orders that are in draft or sent
        status and are marked for merging into an already confirmed sales order,
        thus ensuring that the pickings are created.
        """
        order_not_confirm = orders.filtered(lambda x: x.state in ("sent", "draft"))
        order_not_confirm.action_confirm()
        order_not_confirm.picking_ids.action_assign()

    def merge(self):
        self.ensure_one()
        orders = self.to_merge - self.order_id
        if (
            any(order.state in ("sent", "draft") for order in orders)
            and self.order_id.state == "sale"
        ):
            self._confirm_orders_by_order_target(orders)
        if self.order_id.state == "sale" and orders.mapped("picking_ids"):
            self.merge_pickings()
        if self.order_id.state == "sale" and orders.mapped("invoice_ids"):
            self.merge_moves()
        self.merge_order_lines()
        for order in orders:
            order.with_context(disable_cancel_warning=True).action_cancel()
            order.message_post(body=_("Merged into %(order)s") % {"order": order.name})
        self.order_id.message_post(
            body=_("Order(s) %(orders)s merged into this one")
            % {"orders": ",".join(self.to_merge.mapped("name"))}
        )
        return self.open_sale()
