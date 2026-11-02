# Copyright 2016 Opener B.V. - Stefan Rijnhart
# Copyright 2025 Binhex - Edilio Escalona Almira
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError


class SaleOrderMerge(models.TransientModel):
    _name = "sale.order.merge"
    _description = "Merge sale orders"

    order_id = fields.Many2one(
        "sale.order", "Merge into", required=True, domain="[('id','in',to_merge_ids)]"
    )
    mergeable_ids = fields.Many2many(
        comodel_name="sale.order", related="order_id.merge_with_ids"
    )
    to_merge_ids = fields.Many2many(
        "sale.order",
        "rel_sale_to_merge",
        "sale_id",
        "to_merge_id",
        "Orders to merge",
        domain="[('id','in',mergeable_ids)]",
    )
    message_alert = fields.Boolean(compute="_compute_message_alert", store=True)

    @api.depends("order_id", "to_merge_ids")
    def _compute_message_alert(self):
        for wizard in self:
            wizard.message_alert = wizard.order_id.state in ("draft", "sent") and any(
                order.state == "sale" for order in wizard.to_merge_ids
            )

    def merge_order_lines(self):
        self.order_id.write(
            {
                "order_line": [
                    Command.link(line.id)
                    for line in self.to_merge_ids.mapped("order_line")
                ]
            }
        )

    def merge_moves(self):
        """Merge all draft invoices into one, preferably a draft invoice of
        the target order. Invoices that are not in draft are kept as they are.
        The invoices follow the order lines, so they end up on the target
        order once the lines are merged."""
        orders = self.to_merge_ids - self.order_id
        drafts = (self.order_id.invoice_ids | orders.invoice_ids).filtered(
            lambda move: move.state == "draft"
        )
        if len(drafts) < 2:
            return
        target = drafts[0]
        other_moves = drafts - target
        # Linking through ``line_ids`` lets the target invoice steal the lines,
        # so the taxes and payment terms of both invoices are recomputed.
        target.write(
            {
                "line_ids": [
                    Command.link(line.id) for line in other_moves.invoice_line_ids
                ]
            }
        )
        other_moves.unlink()

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
        pending pickings. In each group of pickings merged together, the one
        of the target order is kept, or the oldest one when it has none."""
        orders = self.to_merge_ids - self.order_id
        own_pickings = self.order_id.picking_ids
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
        self.to_merge_ids.picking_ids.write(
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
            target = (pickings & own_pickings)[:1] or pickings.sorted("id")[:1]
            if len(pickings) > 1:
                pickings -= target
                pickings.move_ids.write({"picking_id": target.id})
                pickings.move_line_ids.write({"picking_id": target.id})
                pickings.unlink()
            target.write({"origin": group.name})
        return True

    def _confirm_orders_by_order_target(self, orders):
        """
        This method allows you to confirm sales orders that are in draft or sent
        status and are marked for merging into an already confirmed sales order,
        thus ensuring that the pickings are created. Confirming locks them when
        confirmed orders are locked, so they are unlocked again to be cancelled.
        """
        order_not_confirm = orders.filtered(lambda x: x.state in ("sent", "draft"))
        order_not_confirm.action_confirm()
        order_not_confirm.picking_ids.action_assign()
        order_not_confirm.filtered("locked").action_unlock()

    def _check_orders_unlocked(self, orders):
        """The merged orders are cancelled, and a locked order cannot be."""
        locked_orders = orders.filtered("locked")
        if locked_orders:
            raise UserError(
                _("Unlock the orders %(orders)s before merging them.")
                % {"orders": ", ".join(locked_orders.mapped("name"))}
            )

    def _get_merge_result_action(self):
        """Action run once the orders are merged. Closing the wizard reloads
        the view it was opened from, so the merged order is shown without
        stacking a new breadcrumb."""
        self.ensure_one()
        return {"type": "ir.actions.act_window_close"}

    def merge(self):
        self.ensure_one()
        orders = self.to_merge_ids - self.order_id
        self._check_orders_unlocked(orders)
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
            order.message_post(
                body=_("Merged into %(order)s") % {"order": self.order_id.name}
            )
        self.order_id.message_post(
            body=_("Order(s) %(orders)s merged into this one")
            % {"orders": ", ".join(orders.mapped("name"))}
        )
        return self._get_merge_result_action()
