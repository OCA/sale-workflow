# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        """
        If partial confirmation feature is enabled,
        instead of standard SO confirmation at first we need
        to open the partial confirmation wizard for current SO.

        If feature is disabled or 'standard_confirm_proceed' context key
        was specified as True, then we proceed with standard confirmation.
        """

        force_confirm = self.env.context.get("standard_confirm_proceed", False)
        partial_confirm_enabled = self.env["ir.config_parameter"].get_param(
            "sale_order_confirm_partial.enabled",
            False,
        )
        if force_confirm or not partial_confirm_enabled:
            return super().action_confirm()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "sale_order_confirm_partial.sale_order_confirm_partial_action"
        )
        action.update(
            {
                "context": {
                    "default_sale_order_id": self.id,
                }
            }
        )
        return action

    def _process_unconfirmed_quotation(self, confirmed_lines):
        """
        If 'Save Unconfirmed Items' feature is enabled,
        then create a new quotation in the 'Cancel' state
        and move all unconfirmed lines to it.

        Quantities of those lines should be reduced
        depending on confirmed quantities.

        If after reduction the quantity of any line
        is less than or equal to 0, then remove that line.

        Args:
            confirmed_lines: sale.order.confirm.partial.line recordset.
            Lines to be confirmed.

        Returns:
            sale.order: Created unconfirmed quotation
            None: If feature is disabled or no unconfirmed lines
        """
        self.ensure_one()
        save_unconfirmed = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_order_confirm_partial.save_unconfirmed", False)
        )
        if not save_unconfirmed:
            return
        # If all lines are confirmed and confirmed quantity
        # is equal to ordered quantity, then no need to create
        # unconfirmed quotation.
        if all(
            [
                line.confirmed_qty == line.so_line_id.product_uom_qty
                for line in confirmed_lines
            ]
        ) and len(confirmed_lines) == len(self.order_line):
            return
        unconfirmed_suffix = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_order_confirm_partial.unconfirmed_suffix", "-U")
        )
        unconfirmed_order = self.copy(
            {
                "name": self.name + unconfirmed_suffix,
                "order_line": False,
            }
        )
        unconfirmed_lines = self.env["sale.order.line"]
        for line in self.order_line:
            confirmed_line = confirmed_lines.filtered(lambda x: x.so_line_id == line)
            if confirmed_line.confirmed_qty == line.product_uom_qty:
                continue
            unconfirmed_lines |= line.copy(
                {
                    "order_id": unconfirmed_order.id,
                    "product_uom_qty": line.product_uom_qty
                    - confirmed_line.confirmed_qty,
                }
            )
        unconfirmed_order.state = "cancel"
        unconfirmed_order.message_post(
            body=_(
                "Created from "
                "<a href=# data-oe-model=sale.order data-oe-id=%(id)d>%(name)s</a>"
            )
            % {"id": self.id, "name": self.name},
            partner_id=self.env.ref("base.partner_root").id,
            subtype_id=self.env.ref("mail.mt_note").id,
        )
        return unconfirmed_order

    def _update_order_lines_qty(self, confirmed_lines):
        """
        Update quantities of order lines depending
        on confirmed quantities in selected lines.

        Args:
            confirmed_lines: sale.order.confirm.partial.line recordset.
        """
        self.ensure_one()
        for line in confirmed_lines:
            line.so_line_id.product_uom_qty = line.confirmed_qty

    def action_confirm_partial(self, confirmed_lines):
        """
        Confirms only selected lines of the SO.

        If 'Save Unconfirmed Items' feature is enabled,
        then it creates also a new quotation in the 'Cancel' state
        containing all unconfirmed lines and quantities.

        Args:
            confirmed_lines: sale.order.confirm.partial.line recordset.
            Lines to be confirmed.
        """
        self.ensure_one()
        unconfirmed_quotation = self._process_unconfirmed_quotation(confirmed_lines)
        self._update_order_lines_qty(confirmed_lines)
        self.with_context(standard_confirm_proceed=True).action_confirm()
        if unconfirmed_quotation:
            self.message_post(
                body=_(
                    "Unconfirmed lines are saved in "
                    "<a href=# data-oe-model=sale.order data-oe-id=%(id)d>%(name)s</a>"
                )
                % {"id": unconfirmed_quotation.id, "name": unconfirmed_quotation.name},
                partner_id=self.env.ref("base.partner_root").id,
                subtype_id=self.env.ref("mail.mt_note").id,
            )
