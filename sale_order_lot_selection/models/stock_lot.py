# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import AccessError


class StockLot(models.Model):
    _inherit = "stock.lot"

    def action_add_to_sale_order(self):
        """Open the wizard to add lots to a sale order."""
        self.ensure_one()
        return self.action_generate_sale_order()

    def action_generate_sale_order(self):
        """Open wizard to generate sale order from lots."""
        if (
            not self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_order_lot_selection.allow_generate_from_lots")
        ):
            raise AccessError(_("You are not allowed to generate Sale Order from Lot."))

        wizard = self.env["stock.lot.sale.order.wizard"].create(
            {
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "lot_id": lot.id,
                            "quantity": lot.product_qty,
                        },
                    )
                    for lot in self
                ]
            }
        )

        return {
            "name": _("Add Lot to Sale Order"),
            "type": "ir.actions.act_window",
            "res_model": "stock.lot.sale.order.wizard",
            "view_mode": "form",
            "res_id": wizard.id,
            "target": "new",
        }
