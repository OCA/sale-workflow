# Copyright 2026 Juan Carlos Oñate - Tecnativa <juancarlos.onate@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from markupsafe import Markup

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_partners_to_check_for_block(self, rule=None):
        self.ensure_one()
        scope = rule.partner_scope if rule else "all"
        if scope == "delivery":
            return self.partner_shipping_id
        if scope == "invoice":
            return self.partner_id | self.partner_invoice_id
        return self.partner_id | self.partner_invoice_id | self.partner_shipping_id

    def _find_blocking_rule(self):
        """Return (rule, partner, message, field_name, field_value) for the first
        active rule that matches any of the order's partners, or None."""
        self.ensure_one()
        rules = self.env["sale.order.block.rule"].search([])
        for rule in rules:
            for partner in self._get_partners_to_check_for_block(rule):
                is_blocked, message, field_name, field_value = (
                    rule._check_partner_blocked(partner)
                )
                if is_blocked:
                    return rule, partner, message, field_name, field_value
        return None

    def _post_partner_block_message(
        self, action_label, rule, partner, message, field_name, field_value
    ):
        self.ensure_one()
        self.message_post(
            body=Markup(
                """
                ⚠️ <strong>%(action)s - Block Rule Triggered</strong>
                <br/><br/>
                <strong>Rule:</strong> %(rule)s<br/>
                <strong>Reason:</strong> %(reason)s<br/>
                <strong>Partner:</strong> %(partner)s<br/>
                <strong>%(field_name)s:</strong> %(field_value)s
                """
            )
            % {
                "action": action_label,
                "rule": rule.name,
                "reason": message,
                "partner": partner.name,
                "field_name": field_name,
                "field_value": field_value,
            },
            subtype_id=self.env.ref("mail.mt_note").id,
        )

    def _apply_partner_block_rule(
        self, rule, partner, message, field_name, field_value
    ):
        """Default action: cancel the order and post the chatter message.
        Override in submodules to implement alternative actions."""
        self.ensure_one()
        self._post_partner_block_message(
            "Order Auto-Canceled", rule, partner, message, field_name, field_value
        )
        self._action_cancel()

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        for order in orders:
            if order.state == "cancel":
                continue
            match = order._find_blocking_rule()
            if match:
                order._apply_partner_block_rule(*match)
        return orders
