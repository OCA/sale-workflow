# Copyright 2016 Opener B.V. - Stefan Rijnhart
# Copyright 2025 Binhex - Edilio Escalona Almira
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import Command, _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    merge_ok = fields.Boolean(
        "Has candidates to merge with", compute="_compute_merge_ok"
    )
    merge_with_ids = fields.Many2many(
        comodel_name="sale.order",
        compute="_compute_merge_with_ids",
        search="_search_merge_with_ids",
        string="Can be merged with",
    )

    def _merge_order_by_states(self):
        states = ["draft", "sent"]
        if (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_order_merge.merge_order_confirm", False)
        ):
            states.append("sale")
        return states

    @api.model
    def _get_merge_depends(self):
        """Fields of the order read by the merge criteria, so the merge
        candidates are computed again when they change. Extend it along with
        ``_can_merge`` and ``_get_merge_domain``."""
        return [
            "state",
            "order_line",
            "partner_id",
            "partner_shipping_id",
            "warehouse_id",
            "company_id",
            "currency_id",
        ]

    def _get_merge_candidates_domain(self):
        """Domain of the other orders this order can be merged with."""
        self.ensure_one()
        return self._search_merge_criteria(add_domain=[("id", "!=", self._origin.id)])

    @api.depends(lambda self: self._get_merge_depends())
    def _compute_merge_ok(self):
        """Not stored: the candidates also depend on the other orders of the
        database, which no dependency can follow, so the value is only
        reliable when read in a new request. A count limited to one record
        is enough to show the merge button."""
        for sale in self:
            sale.merge_ok = bool(
                self.search_count(sale._get_merge_candidates_domain(), limit=1)
            )

    @api.depends(lambda self: self._get_merge_depends())
    def _compute_merge_with_ids(self):
        """Not stored, for the same reason as ``merge_ok``. It runs one
        search per order, so it is meant to be read on a single order, as
        the merge wizard does."""
        for sale in self:
            sale.merge_with_ids = self.search(sale._get_merge_candidates_domain())

    def _can_merge(self, states=None):
        """Conditions an order must meet to be merged"""
        self.ensure_one()
        if states is None:
            states = self._merge_order_by_states()
        return self.state in states and self.order_line

    def _get_merge_domain(self, states=None):
        """Domain of the orders that meet the merge criteria of this order"""
        if states is None:
            states = self._merge_order_by_states()
        return [
            ("partner_id", "=", self.partner_id.id),
            ("partner_shipping_id", "=", self.partner_shipping_id.id),
            ("warehouse_id", "=", self.warehouse_id.id),
            ("company_id", "=", self.company_id.id),
            ("currency_id", "=", self.currency_id.id),
            ("state", "in", states),
        ]

    def _search_merge_criteria(self, add_domain=None):
        states = self._merge_order_by_states()
        if not self._can_merge(states):
            return [("id", "=", False)]
        domain = self._get_merge_domain(states)
        if add_domain:
            domain += add_domain
        return domain

    def _search_merge_with_ids(self, operator, value):
        """Apply criteria with which other sale orders the given order
        is mergeable."""
        if operator != "=" or not isinstance(value, int):
            raise NotImplementedError(
                _("Operation not supported: %(operator)s %(value)s")
                % {"operator": operator, "value": value}
            )
        return self.browse(value)._get_merge_candidates_domain()

    def _message_error(self, order_target, states):
        message = ""
        group_partner = defaultdict(list)
        group_partner_shipping = defaultdict(list)
        group_warehouse = defaultdict(list)
        group_company = defaultdict(list)
        group_currency = defaultdict(list)
        group_states = defaultdict(list)
        merge_states = self._merge_order_by_states()
        for order in self:
            if order_target.partner_id != order.partner_id:
                group_partner[order.partner_id].append(order)
            if order_target.partner_shipping_id != order.partner_shipping_id:
                group_partner_shipping[order.partner_shipping_id].append(order)
            if order_target.warehouse_id != order.warehouse_id:
                group_warehouse[order.warehouse_id].append(order)
            if order_target.company_id != order.company_id:
                group_company[order.company_id].append(order)
            if order_target.currency_id != order.currency_id:
                group_currency[order.currency_id].append(order)
            if order.state not in merge_states:
                group_states[states.get(order.state)].append(order)

        message += _("\nState - Orders") if group_states else ""
        for state, orders in group_states.items():
            message += _("\n\u2003%(state)s:\u2009\u2009%(orders)s") % {
                "state": state,
                "orders": ", ".join(list(map(lambda x: x.name, orders))),
            }

        message += _("\nPartner - Orders") if group_partner else ""
        for partner, orders in group_partner.items():
            message += _("\n\u2003%(partner)s:\u2009\u2009%(orders)s") % {
                "partner": partner.name,
                "orders": ", ".join(list(map(lambda x: x.name, orders))),
            }

        message += _("\nDelivery address - Orders") if group_partner_shipping else ""
        for delivery, orders in group_partner_shipping.items():
            message += _("\n\u2003%(delivery)s:\u2009\u2009%(orders)s") % {
                "delivery": delivery.name,
                "orders": ", ".join(list(map(lambda x: x.name, orders))),
            }

        message += _("\nWarehouse - Orders") if group_warehouse else ""
        for warehouse, orders in group_warehouse.items():
            message += _("\n\u2003%(warehouse)s:\u2009\u2009%(orders)s") % {
                "warehouse": warehouse.name,
                "orders": ", ".join(list(map(lambda x: x.name, orders))),
            }

        message += _("\nCompany - Orders") if group_company else ""
        for company, orders in group_company.items():
            message += _("\n\u2003%(company)s:\u2009\u2009%(orders)s") % {
                "company": company.name,
                "orders": ", ".join(list(map(lambda x: x.name, orders))),
            }

        message += _("\nCurrency - Orders") if group_currency else ""
        for currency, orders in group_currency.items():
            message += _("\n\u2003%(currency)s:\u2009\u2009%(orders)s") % {
                "currency": currency.name,
                "orders": ", ".join(list(map(lambda x: x.name, orders))),
            }
        return message

    def _validate_selected(self, order_target):
        states = {k: v for k, v in dict(self._fields["state"].selection).items()}
        message = self._message_error(order_target, states)
        if message:
            message_error = _(
                "Some selected orders do not meet the merge criteria "
                "(partner, delivery address, warehouse, company, "
                "currency, order status) "
                "with the target order %(order_target)s"
                " (the first one created among the selected orders in any "
                "of the %(states)s statuses), detailed below:\n%(message)s"
            ) % {
                "order_target": order_target.name,
                "states": ", ".join(
                    [states.get(val) for val in self._merge_order_by_states()]
                ),
                "message": message,
            }
            raise ValidationError(message_error)

    def _get_order_by_orderby(self, criteria="create_date", strategy=True):
        states = self._merge_order_by_states()
        return self.filtered(lambda x: x.state in states).sorted(
            criteria, reverse=strategy
        )

    def action_button_merge(self):
        order = self._get_order_by_orderby()[-1]
        add_domain = [("id", "in", self.ids)] if len(self) > 1 else None
        merge_orders = self.search(order._search_merge_criteria(add_domain=add_domain))
        if len(self) > 1:
            (self - merge_orders)._validate_selected(order)

        wizard_merge = self.env["sale.order.merge"].create(
            {
                "order_id": order.id,
                "to_merge_ids": [Command.set(merge_orders.ids)],
            }
        )
        return {
            "name": _("Merge sale orders"),
            "view_mode": "form",
            "res_model": "sale.order.merge",
            "res_id": wizard_merge.id,
            "type": "ir.actions.act_window",
            "target": "new",
        }
