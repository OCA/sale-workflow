from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


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
    has_valid_delivery_request = fields.Boolean(
        compute="_compute_has_valid_delivery_request",
    )
    has_delivery_request = fields.Boolean(
        compute="_compute_has_delivery_request",
    )

    @api.depends("delivery_request_ids")
    def _compute_delivery_request_count(self):
        for order in self:
            order.delivery_request_count = len(order.delivery_request_ids)

    @api.depends("delivery_request_ids.state")
    def _compute_has_valid_delivery_request(self):
        for order in self:
            order.has_valid_delivery_request = any(
                req.state == "confirmed" for req in order.delivery_request_ids
            )

    @api.depends("delivery_request_ids")
    def _compute_has_delivery_request(self):
        for order in self:
            order.has_delivery_request = bool(order.delivery_request_ids)

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
            notification_params = {
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
                if final_date:
                    sol.with_context(from_delivery_request=True).write(
                        {
                            "commitment_date": fields.Datetime.to_datetime(final_date),
                            "commitment_date_from_dr": True,
                        }
                    )
                continue

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
                    }
                )
                req_line.sale_order_line_id = new_sol

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
