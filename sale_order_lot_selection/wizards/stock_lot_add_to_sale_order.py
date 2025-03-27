# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockLotSaleOrderWizard(models.TransientModel):
    _name = "stock.lot.sale.order.wizard"
    _description = "Add Lot to Sale Order Wizard"

    line_ids = fields.One2many(
        "stock.lot.sale.order.wizard.line",
        "wizard_id",
        string="Lot Lines",
        ondelete="cascade",
    )

    sale_order_id = fields.Many2one(
        "sale.order",
        string="Sale Order",
        domain="[('state', 'not in', ['done', 'cancel'])]",
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
        store=True,
        compute="_compute_partner_id",
    )

    @api.depends("sale_order_id")
    def _compute_partner_id(self):
        for record in self:
            record.partner_id = record.sale_order_id.partner_id.id

    def action_add_lots_to_sale_order(self):
        """Add selected lots to the existing sale order."""
        self.ensure_one()
        if not self.sale_order_id:
            raise ValidationError(
                _("Please select an existing Sale Order to add lots to.")
            )
        self.sale_order_id.write(
            {
                "order_line": self._prepare_sale_order_line_vals(),
            }
        )
        return self._action_open_sale_order()

    def action_create_sale_order(self):
        """Create a sale order from the selected lots."""
        self.ensure_one()
        if not self.partner_id:
            raise ValidationError(
                _("Please select a customer to create a new Sale Order.")
            )
        self.sale_order_id = self.env["sale.order"].create(
            {
                "partner_id": self.partner_id.id,
                "order_line": self._prepare_sale_order_line_vals(),
            }
        )
        return self._action_open_sale_order()

    def _prepare_sale_order_line_vals(self):
        """Get values for adding lot in sale order line."""
        if not self.line_ids:
            raise ValidationError(_("Please select at least one lot."))
        return [
            (
                0,
                0,
                {
                    "lot_id": line.lot_id.id,
                    "product_id": line.lot_id.product_id.id,
                    "product_uom_qty": line.quantity,
                },
            )
            for line in self.line_ids
        ]

    def _action_open_sale_order(self):
        """Open the sale order form view."""
        return {
            "type": "ir.actions.act_window",
            "name": "Sale Order",
            "res_model": "sale.order",
            "view_mode": "form",
            "res_id": self.sale_order_id.id,
            "target": "current",
        }
