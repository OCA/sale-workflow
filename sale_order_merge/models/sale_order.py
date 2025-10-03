# Copyright 2016 Opener B.V. - Stefan Rijnhart
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import Command, _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    merge_ok = fields.Boolean(
        "Has candidates to merge with", compute="_compute_merge_ok"
    )
    merge_with = fields.Many2many(
        comodel_name="sale.order",
        compute="_compute_merge_with",
        search="_search_merge_with",
        string="Can be merged with",
    )

    def _merge_order_by_states(self):
        states = ["draft"]
        if (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_order_merge.merge_order_confirm", False)
        ):
            states.append("sale")
        return states

    @api.depends("merge_with")
    def _compute_merge_ok(self):
        for sale in self:
            sale.merge_ok = bool(sale.merge_with)

    def _compute_merge_with(self):
        for sale in self:
            sale.merge_with = self.search([("merge_with", "=", sale.id)])

    def _can_merge(self):
        """Hook for redefining merge conditions"""
        self.ensure_one()
        return self.state in self._merge_order_by_states() and self.order_line

    def _get_merge_domain(self):
        """Hook for redefining merge conditions"""
        return [
            ("partner_id", "=", self.partner_id.id),
            ("partner_shipping_id", "=", self.partner_shipping_id.id),
            ("warehouse_id", "=", self.warehouse_id.id),
            ("company_id", "=", self.company_id.id),
            ("currency_id", "=", self.currency_id.id),
            ("state", "in", self._merge_order_by_states()),
        ]

    def _search_merge_criteria(self, add_domain=None):
        if not self._can_merge():
            return [("id", "=", False)]
        domain = self._get_merge_domain()
        if add_domain:
            domain += add_domain
        return domain

    def _search_merge_with(self, op, arg):
        """Apply criteria with which other sale orders the given order
        is mergeable."""
        return self._search_merge_criteria()

    def _get_orders_selected(self):
        order_groups = self._read_group(
            [("id", "in", self.ids)],
            ["id"],
            [
                "partner_id:recordset",
                "partner_shipping_id:recordset",
                "warehouse_id:recordset",
                "company_id:recordset",
                "currency_id:recordset",
            ],
        )
        return order_groups

    def _message_error(self, order_target, states):
        message = ""
        group_partner = defaultdict(list)
        group_partner_shipping = defaultdict(list)
        group_warehouse = defaultdict(list)
        group_company = defaultdict(list)
        group_currency = defaultdict(list)
        group_states = defaultdict(list)
        order_groups = self._get_orders_selected()
        for order, partner, shipping, warehouse, company, currency in order_groups:
            if order_target.partner_id != partner:
                group_partner[partner].append(order)
            if order_target.partner_shipping_id != shipping:
                group_partner_shipping[shipping].append(order)
            if order_target.warehouse_id != warehouse:
                group_warehouse[warehouse].append(order)
            if order_target.company_id != company:
                group_company[company].append(order)
            if order_target.currency_id != currency:
                group_currency[currency].append(order)
            if order.state not in self._merge_order_by_states():
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
                " (the last one created from the selected ones and has any "
                "of the %(states)s statuses), detailed below:\n%(message)s"
            ) % {
                "order_target": order_target.name,
                "states": ",".join(
                    [states.get(val) for val in self._merge_order_by_states()]
                ),
                "message": message,
            }
            raise ValidationError(message_error)

    def _get_order_by_orderby(self, criteria="create_date", strategy=True):
        return self.filtered(lambda x: x.state in self._merge_order_by_states()).sorted(
            criteria, reverse=strategy
        )

    def action_button_merge(self):
        order = self._get_order_by_orderby()[-1]
        domain = [("merge_with", "=", order.id)]
        if len(self) > 1:
            domain = order._search_merge_criteria(add_domain=[("id", "in", self.ids)])
        merge_ids = self.search(domain)
        if len(self) > 1:
            (self - merge_ids)._validate_selected(order)

        wizard_merge = self.env["sale.order.merge"].create(
            {
                "order_id": order.id,
                "to_merge": [Command.set(merge_ids.ids)],
            }
        )
        return {
            "name": _("Merge sale orders"),
            "view_type": "form",
            "view_mode": "form",
            "res_model": "sale.order.merge",
            "res_id": wizard_merge.id,
            "type": "ir.actions.act_window",
            "target": "new",
        }
