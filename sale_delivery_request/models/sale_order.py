from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"

    delivery_request_ids = fields.One2many(
        comodel_name="sale.delivery.request",
        inverse_name="sale_order_id",
        string="Delivery Requests",
    )
    delivery_request_count = fields.Integer(
        compute="_compute_delivery_request_count",
    )
    has_pending_delivery_request = fields.Boolean(
        compute="_compute_has_pending_delivery_request",
    )

    @api.depends("delivery_request_ids")
    def _compute_delivery_request_count(self):
        for order in self:
            order.delivery_request_count = len(order.delivery_request_ids)

    @api.depends("delivery_request_ids.state")
    def _compute_has_pending_delivery_request(self):
        for order in self:
            order.has_pending_delivery_request = any(
                req.state in ("draft", "pending") for req in order.delivery_request_ids
            )

    def action_request_delivery_date(self):
        """
        Create a new sale.delivery.request from the current SO
        """
        self.ensure_one()
        request_vals = {
            "sale_order_id": self.id,
            "request_datetime": fields.Datetime.now(),
            "state": "pending",
        }
        line_vals = []
        for sol in self.order_line.filtered(
            lambda x: not x.display_type and x.product_id.type in ("consu", "product")
        ):
            remaining = sol.product_uom_qty - sol.qty_delivered
            if remaining > 0:
                line_vals.append(
                    (
                        0,
                        0,
                        {
                            "sale_order_line_id": sol.id,
                            "quantity": remaining,
                        },
                    )
                )
        if not line_vals:
            raise UserError(_("No lines with remaining quantity to request."))
        request_vals["line_ids"] = line_vals
        request = self.env["sale.delivery.request"].create(request_vals)
        return {
            "name": _("Delivery Request"),
            "type": "ir.actions.act_window",
            "res_model": "sale.delivery.request",
            "res_id": request.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_view_delivery_requests(self):
        self.ensure_one()
        action = {
            "name": _("Delivery Requests"),
            "type": "ir.actions.act_window",
            "res_model": "sale.delivery.request",
            "context": {"default_sale_order_id": self.id},
        }
        requests = self.delivery_request_ids
        if len(requests) == 1:
            action["view_mode"] = "form"
            action["res_id"] = requests.id
        else:
            action["view_mode"] = "tree,form"
            action["domain"] = [("id", "in", requests.ids)]
        return action

    def action_confirm(self):
        """
        Extends the standard confirmation to handle expired delivery requests.

        If all delivery requests are expired, a new priority request is created
        and the SO is NOT confirmed — the user must wait for Planning to confirm
        the new request. A notification is returned to the client instead.

        Pending-DR blocking and date application are handled in _action_confirm.
        """
        notification_params = self._get_expired_dr_notification()
        if notification_params:
            notification_params["next"] = {
                "type": "ir.actions.client",
                "tag": "soft_reload",
            }
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": notification_params,
            }
        return super().action_confirm()

    def _get_expired_dr_notification(self):
        """
        If any order in self has only expired delivery requests (no valid
        confirmed one), auto-expire date-lapsed requests, create a new priority
        request, and return notification params to show the user.

        Returns a dict of notification params if blocking is needed, else None.
        When multiple orders are affected, a single notification lists all of
        them.
        """
        expired_order_messages = []
        for order in self:
            confirmed_requests = order.delivery_request_ids.filtered(
                lambda r: r.state == "confirmed"
            )
            expired_requests = order.delivery_request_ids.filtered(
                lambda r: r.state == "expired"
            )
            pending_requests = order.delivery_request_ids.filtered(
                lambda r: r.state in ("draft", "pending")
            )
            if pending_requests:
                continue
            if not confirmed_requests and not expired_requests:
                continue

            today = fields.Date.context_today(order)

            date_lapsed = confirmed_requests.filtered(
                lambda r, today=today: r.expiration_date and r.expiration_date < today
            )
            if date_lapsed:
                date_lapsed.write({"state": "expired"})
                expired_requests |= date_lapsed
                confirmed_requests -= date_lapsed

            valid_request = next(
                (
                    req
                    for req in confirmed_requests
                    if not req.expiration_date or req.expiration_date >= today
                ),
                False,
            )

            if not valid_request:
                all_expired = confirmed_requests | expired_requests
                latest_expired = all_expired.sorted("response_datetime", reverse=True)[
                    0
                ]
                new_req = latest_expired._create_priority_request()
                order.message_post(
                    body=_(
                        "The delivery date confirmation has expired. "
                        "A new priority request (%(name)s) has been created.",
                        name=new_req.name,
                    ),
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                )
                expired_order_messages.append(
                    _("%(order)s → %(request)s", order=order.name, request=new_req.name)
                )

        if not expired_order_messages:
            return None

        return {
            "title": _("Delivery Request Expired"),
            "message": _(
                "The delivery date confirmation has expired. "
                "New priority requests have been created. "
                "Please wait for Planning confirmation.\n%(details)s",
                details="\n".join(expired_order_messages),
            ),
            "type": "warning",
            "sticky": True,
        }

    def _action_cancel(self):
        for order in self:
            active_requests = order.delivery_request_ids.filtered(
                lambda r: r.state not in ("cancel", "confirmed", "expired")
            )
            active_requests.action_cancel()
        return super()._action_cancel()

    def _action_confirm(self):
        """
        Blocks confirmation if any delivery request is still pending.
        Delivery dates are already applied when the DR is confirmed.
        """
        for order in self:
            pending_requests = order.delivery_request_ids.filtered(
                lambda r: r.state in ("draft", "pending")
            )
            if pending_requests:
                raise UserError(
                    _(
                        "Cannot confirm the order: there are pending "
                        "delivery requests (%(names)s). Please wait "
                        "for Planning confirmation.",
                        names=", ".join(pending_requests.mapped("name")),
                    )
                )

        return super()._action_confirm()

    def _compute_delivery_request_final_date(
        self, delivery_request, offset, confirmation_dt=None
    ):
        """
        Return a date computed from business-day offset, or False.
        """
        self.ensure_one()
        if not offset:
            return False

        confirmation_dt = confirmation_dt or fields.Datetime.now()
        calendar = delivery_request._get_calendar()

        if calendar:
            result_dt = calendar.plan_days(offset, confirmation_dt, compute_leaves=True)
            return result_dt.date() if result_dt else False

        return self._add_business_days_simple(confirmation_dt.date(), offset)

    def _apply_delivery_request_dates(self, delivery_request):
        """
        Recalculate delivery dates and split SOLs when needed so that
        it handles procurement grouping and picking splitting correctly.

        When multiple DR lines share the same SOL (i.e. the line was split
        in the delivery request), we:
        1. Keep the original SOL for the group with the largest quantity,
           adjusting its product_uom_qty and commitment_date.
        2. Create new SOLs for every other group, each with its
           own product_uom_qty and commitment_date.
        3. Re-point the DR lines to the correct SOL so the relationship
           stays consistent.
        """
        self.ensure_one()
        confirmation_dt = fields.Datetime.now()
        sol_groups = {}
        for req_line in delivery_request.line_ids:
            sol_groups.setdefault(req_line.sale_order_line_id.id, []).append(req_line)

        for _sol_id, req_lines in sol_groups.items():
            sol = req_lines[0].sale_order_line_id

            if len(req_lines) == 1:
                req_line = req_lines[0]
                final_date = self._compute_delivery_request_final_date(
                    delivery_request,
                    req_line.business_days_offset,
                    confirmation_dt=confirmation_dt,
                )
                sol_vals = {"commitment_date_from_dr": True}
                if final_date:
                    sol_vals["commitment_date"] = fields.Datetime.to_datetime(
                        final_date
                    )
                # After a cross-DR merge the DR line qty may exceed the
                # SOL qty — sync it before confirmation creates procurements.
                precision = self.env["decimal.precision"].precision_get(
                    "Product Unit of Measure"
                )
                if (
                    float_compare(
                        req_line.quantity,
                        sol.product_uom_qty,
                        precision_digits=precision,
                    )
                    != 0
                ):
                    sol_vals["product_uom_qty"] = req_line.quantity
                    # Clean up orphaned split SOLs from previous DRs
                    # that have been merged back into the original.
                    orphan_sols = self.env["sale.order.line"].search(
                        [
                            ("original_line_id", "=", sol.id),
                            ("order_id", "=", self.id),
                        ]
                    )
                    if orphan_sols:
                        orphan_sols.unlink()
                sol.with_context(from_delivery_request=True).write(sol_vals)
                continue

            # Clean up orphaned split SOLs from previous DRs (cross-DR merge
            # scenario) before creating new splits.
            orphan_sols = self.env["sale.order.line"].search(
                [
                    ("original_line_id", "=", sol.id),
                    ("order_id", "=", self.id),
                ]
            )
            if orphan_sols:
                orphan_sols.unlink()

            req_lines_sorted = sorted(req_lines, key=lambda x: x.quantity, reverse=True)
            keep_line, split_lines = req_lines_sorted[0], req_lines_sorted[1:]

            keep_date = self._compute_delivery_request_final_date(
                delivery_request,
                keep_line.business_days_offset,
                confirmation_dt=confirmation_dt,
            )
            sol.with_context(from_delivery_request=True).write(
                {
                    "product_uom_qty": keep_line.quantity,
                    "commitment_date": fields.Datetime.to_datetime(keep_date)
                    if keep_date
                    else False,
                    "commitment_date_from_dr": True,
                }
            )

            for req_line in split_lines:
                split_date = self._compute_delivery_request_final_date(
                    delivery_request,
                    req_line.business_days_offset,
                    confirmation_dt=confirmation_dt,
                )
                new_sol = sol.with_context(from_delivery_request=True).copy(
                    {
                        "order_id": self.id,
                        "product_uom_qty": req_line.quantity,
                        "commitment_date": fields.Datetime.to_datetime(split_date)
                        if split_date
                        else False,
                        "commitment_date_from_dr": True,
                        "original_line_id": sol.id,
                    }
                )
                req_line.sale_order_line_id = new_sol

    def _sol_needs_reschedule(self, sol, target_date, target_qty):
        """
        Return True if the SOL's existing active outbound move differs from the
        target date or target quantity, meaning a cancel+relaunch is needed.

        ``target_date`` is a ``date`` object (or False).
        ``target_qty``  is a float in the SOL's UoM (or False to skip qty check).

        Comparison rules:
        - Date: compare at date level (ignore time component).
        - Qty:  compare using Product Unit of Measure precision.
        If no active outbound move exists, always reschedule (procurement not yet run).
        """
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        active_out_moves = sol.move_ids.filtered(
            lambda m: m.state not in ("cancel", "done")
            and m.location_dest_id.usage == "customer"
        )
        if not active_out_moves:
            return True

        if target_date:
            for move in active_out_moves:
                move_date = move.date_deadline.date() if move.date_deadline else False
                if move_date != target_date:
                    return True

        if target_qty is not False:
            total_out_qty = sum(
                m.product_uom._compute_quantity(
                    m.product_uom_qty, sol.product_uom, rounding_method="HALF-UP"
                )
                for m in active_out_moves
            )
            if (
                float_compare(total_out_qty, target_qty, precision_digits=precision)
                != 0
            ):
                return True

        return False

    def _cancel_move_chain(self, sol):
        """
        Cancel all cancellable moves in the full move chain of a SOL
        and return the pickings that were affected.

        Returns (True, affected_pickings) if the chain was clean, or
        (False, empty) if reserved moves were found and the SOL must be skipped.
        """
        full_chain = sol._get_full_move_chain()
        if full_chain.filtered(
            lambda m: m.state in ("assigned", "partially_available")
        ):
            return False, self.env["stock.picking"]
        cancellable = full_chain.filtered(
            lambda m: m.state in ("draft", "waiting", "confirmed")
        )
        affected_pickings = cancellable.picking_id
        if cancellable:
            cancellable._action_cancel()
        return True, affected_pickings

    def _group_delivery_request_lines_for_stock(self, delivery_request):
        sol_groups = {}
        for req_line in delivery_request.line_ids:
            sol = req_line.sale_order_line_id
            if not sol or sol.state != "sale":
                continue
            sol_groups.setdefault(sol.id, []).append(req_line)
        return sol_groups

    def _get_orphan_split_sols(self, sol):
        return self.env["sale.order.line"].search(
            [
                ("original_line_id", "=", sol.id),
                ("order_id", "=", self.id),
            ]
        )

    def _has_reserved_move_chain(self, sol):
        return bool(
            sol._get_full_move_chain().filtered(
                lambda m: m.state in ("assigned", "partially_available")
            )
        )

    def _cancel_orphan_split_sols(self, sol, pickings_to_fence, skipped_products):
        orphan_sols = self._get_orphan_split_sols(sol)
        for orphan in orphan_sols:
            ok_orphan, affected_orphan = self._cancel_move_chain(orphan)
            if ok_orphan:
                pickings_to_fence |= affected_orphan
            else:
                skipped_products.append(orphan.product_id.display_name)
        orphan_sols.filtered(lambda s: not self._has_reserved_move_chain(s)).unlink()
        return pickings_to_fence

    def _apply_delivery_request_stock_single(
        self,
        delivery_request,
        req_line,
        confirmation_dt,
        lines_to_relaunch,
        pickings_to_fence,
        skipped_products,
    ):
        sol = req_line.sale_order_line_id
        final_date = self._compute_delivery_request_final_date(
            delivery_request,
            req_line.business_days_offset,
            confirmation_dt=confirmation_dt,
        )
        if not self._sol_needs_reschedule(sol, final_date, req_line.quantity):
            return lines_to_relaunch, pickings_to_fence

        ok, affected = self._cancel_move_chain(sol)
        if not ok:
            skipped_products.append(sol.product_id.display_name)
            return lines_to_relaunch, pickings_to_fence
        pickings_to_fence |= affected

        sol_vals = {}
        if final_date:
            sol_vals["commitment_date"] = fields.Datetime.to_datetime(final_date)
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        if (
            float_compare(
                req_line.quantity,
                sol.product_uom_qty,
                precision_digits=precision,
            )
            != 0
        ):
            sol_vals["product_uom_qty"] = req_line.quantity
            pickings_to_fence = self._cancel_orphan_split_sols(
                sol, pickings_to_fence, skipped_products
            )
        if sol_vals:
            sol.with_context(
                skip_sol_reschedule=True, from_delivery_request=True
            ).write(sol_vals)
        lines_to_relaunch |= sol
        return lines_to_relaunch, pickings_to_fence

    def _apply_delivery_request_stock_split(
        self,
        delivery_request,
        req_lines,
        confirmation_dt,
        lines_to_relaunch,
        pickings_to_fence,
        skipped_products,
    ):
        sol = req_lines[0].sale_order_line_id
        ok, affected = self._cancel_move_chain(sol)
        if not ok:
            skipped_products.append(sol.product_id.display_name)
            return lines_to_relaunch, pickings_to_fence
        pickings_to_fence |= affected

        pickings_to_fence = self._cancel_orphan_split_sols(
            sol, pickings_to_fence, skipped_products
        )

        req_lines_sorted = sorted(req_lines, key=lambda x: x.quantity, reverse=True)
        keep_req, split_reqs = req_lines_sorted[0], req_lines_sorted[1:]

        keep_date = self._compute_delivery_request_final_date(
            delivery_request,
            keep_req.business_days_offset,
            confirmation_dt=confirmation_dt,
        )
        sol.with_context(
            skip_sol_reschedule=True,
            skip_procurement=True,
            from_delivery_request=True,
        ).write(
            {
                "product_uom_qty": keep_req.quantity,
                "commitment_date": fields.Datetime.to_datetime(keep_date)
                if keep_date
                else False,
            }
        )
        lines_to_relaunch |= sol

        for req_line in split_reqs:
            split_date = self._compute_delivery_request_final_date(
                delivery_request,
                req_line.business_days_offset,
                confirmation_dt=confirmation_dt,
            )
            new_sol = sol.with_context(
                skip_procurement=True, from_delivery_request=True
            ).copy(
                {
                    "order_id": self.id,
                    "product_uom_qty": req_line.quantity,
                    "commitment_date": fields.Datetime.to_datetime(split_date)
                    if split_date
                    else False,
                    "original_line_id": sol.id,
                }
            )
            req_line.sale_order_line_id = new_sol
            lines_to_relaunch |= new_sol
        return lines_to_relaunch, pickings_to_fence

    def _apply_delivery_request_dates_stock(self, delivery_request):
        """
        Apply new delivery dates from a post-confirmation delivery request.

        Decision logic per SOL group:

        No-split (1 DR line → 1 SOL):
          - If the existing outbound move already has the same date AND qty → skip.
          - Otherwise: cancel full move chain + update commitment_date + relaunch
            into new pickings.

        Split (multiple DR lines → same original SOL):
          - The original SOL qty always changes, so always cancel the full chain.
          - Keep the original SOL for the largest-qty group.
          - Create new SOLs for every other group.
          - Relaunch all resulting SOLs into new pickings.
          - Exception: if a resulting SOL's date+qty already matches its existing
            moves (e.g. the "keep" group is unchanged), skip relaunch for it.
        """
        self.ensure_one()
        confirmation_dt = fields.Datetime.now()
        lines_to_relaunch = self.env["sale.order.line"]
        skipped_products = []

        sol_groups = self._group_delivery_request_lines_for_stock(delivery_request)

        pickings_to_fence = self.env["stock.picking"]

        for req_lines in sol_groups.values():
            sol = req_lines[0].sale_order_line_id
            if self._has_reserved_move_chain(sol):
                skipped_products.append(sol.product_id.display_name)
                continue

            if len(req_lines) == 1:
                (
                    lines_to_relaunch,
                    pickings_to_fence,
                ) = self._apply_delivery_request_stock_single(
                    delivery_request,
                    req_lines[0],
                    confirmation_dt,
                    lines_to_relaunch,
                    pickings_to_fence,
                    skipped_products,
                )
                continue

            (
                lines_to_relaunch,
                pickings_to_fence,
            ) = self._apply_delivery_request_stock_split(
                delivery_request,
                req_lines,
                confirmation_dt,
                lines_to_relaunch,
                pickings_to_fence,
                skipped_products,
            )

        if skipped_products:
            self.message_post(
                body=_(
                    "The following sale order lines could not be rescheduled "
                    "because their stock moves are already reserved: %s. "
                    "Please unreserve the related pickings first.",
                    ", ".join(skipped_products),
                ),
                message_type="notification",
                subtype_xmlid="mail.mt_note",
            )

        if lines_to_relaunch:
            # Fence all open pickings in the procurement groups of the lines
            # being relaunched. This prevents _search_picking_for_assignation
            # from merging relaunched moves into existing pickings that have a
            # different scheduled date.
            relaunch_groups = lines_to_relaunch.mapped("order_id.procurement_group_id")
            all_group_pickings = self.env["stock.picking"].search(
                [
                    ("group_id", "in", relaunch_groups.ids),
                    ("state", "not in", ("cancel", "done")),
                ]
            )
            open_to_fence = (pickings_to_fence | all_group_pickings).filtered(
                lambda p: p.state not in ("cancel", "done")
            )
            if open_to_fence:
                open_to_fence.write({"printed": True})
            try:
                lines_to_relaunch._action_launch_stock_rule()
            finally:
                if open_to_fence:
                    open_to_fence.write({"printed": False})

    @staticmethod
    def _add_business_days_simple(start_date, days):
        """Fallback: add N Mon-Fri days to a date."""
        current = start_date
        added = 0
        while added < days:
            current += timedelta(days=1)
            if current.weekday() < 5:
                added += 1
        return current
