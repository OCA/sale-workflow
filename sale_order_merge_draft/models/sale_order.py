# Copyright 2026 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from collections import defaultdict

from odoo import models
from odoo.exceptions import UserError

MERGEABLE_STATES = ("draft", "sent")


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_merge_key(self):
        """Return the values two orders must have in common to be merged.

        ``action_merge`` groups the selected orders on this key and merges each
        group of two or more into a single order. Add an element to forbid
        merging orders that differ on one more field::

            def _prepare_merge_key(self):
                return super()._prepare_merge_key() + (self.event_id.id,)

        The values are used as a dictionary key, so they must be hashable.
        """
        self.ensure_one()
        return (
            self.company_id.id,
            self.partner_id.id,
            self.partner_invoice_id.id,
            self.partner_shipping_id.id,
            self.currency_id.id,
        )

    def _select_merge_target(self):
        """Return the order of ``self`` that survives the merge.

        The oldest one: it keeps its number, its chatter and its own lines, and
        receives the lines of the others.
        """
        return min(self, key=lambda order: order.date_order)

    def _find_mergeable_line(self, line):
        """Return the line of ``self`` that should absorb ``line``.

        An empty recordset means ``line`` has no counterpart here and is moved
        over as a new line. Sections and notes never have a counterpart: they
        are moved as they are, never consolidated.
        """
        self.ensure_one()
        if line.display_type:
            return self.env["sale.order.line"]
        merge_line_key = line._merge_line_key()
        return self.order_line.filtered(
            lambda sol: not sol.display_type and sol._merge_line_key() == merge_line_key
        )[:1]

    def _post_merge_from(self, source_orders):
        """Hook on the order that absorbed the lines of ``source_orders``.

        ``self`` is the surviving order, ``source_orders`` the ones it emptied
        and cancelled. Called last, once the lines and the references have been
        moved over.
        """
        return True

    def _merge_orders(self):
        """Merge ``self``, a group of compatible orders, and return the survivor.

        Called once per group by ``action_merge``. Every line of the other
        orders is either absorbed by a matching line of the survivor or moved
        onto it, after its existing lines; the emptied orders are cancelled.
        """
        target_order = self._select_merge_target()
        source_orders = self - target_order
        sequence = max(target_order.order_line.mapped("sequence"), default=0)
        source_lines = source_orders.order_line.sorted(
            lambda sol: (sol.order_id.id, sol.sequence, sol.id)
        )
        for line in source_lines:
            mergeable_line = target_order._find_mergeable_line(line)
            if mergeable_line:
                mergeable_line._merge_sale_line(line)
                line.unlink()
            else:
                sequence += 1
                line._move_to_order(target_order, sequence)
        for field_name in ("origin", "client_order_ref"):
            references = dict.fromkeys(
                filter(None, (target_order | source_orders).mapped(field_name))
            )
            target_order[field_name] = ", ".join(references) or False
        target_order.message_post(
            body=self.env._(
                "Merged with %s",
                ", ".join(order._get_html_link() for order in source_orders),
            )
        )
        for source_order in source_orders:
            source_order.message_post(
                body=self.env._("Merged into %s", target_order._get_html_link())
            )
        source_orders._action_cancel()
        target_order._post_merge_from(source_orders)
        return target_order

    def action_merge(self):
        """Merge the selected quotations, group by group, and show the result."""
        orders_by_merge_key = defaultdict(lambda: self.browse())
        for order in self:
            if order.state not in MERGEABLE_STATES:
                continue
            orders_by_merge_key[order._prepare_merge_key()] |= order
        if sum(len(orders) for orders in orders_by_merge_key.values()) < 2:
            raise UserError(
                self.env._(
                    "Please select at least two quotations in state Quotation or "
                    "Quotation Sent to merge."
                )
            )
        groups_to_merge = [
            orders for orders in orders_by_merge_key.values() if len(orders) > 1
        ]
        if not groups_to_merge:
            raise UserError(
                self.env._(
                    "None of the selected quotations are compatible with each "
                    "other. Quotations can only be merged when they share the "
                    "same customer and the same order settings."
                )
            )
        merged_orders = self.browse()
        for orders in groups_to_merge:
            merged_orders |= orders._merge_orders()
        return merged_orders._get_records_action(name=self.env._("Merged Quotations"))
