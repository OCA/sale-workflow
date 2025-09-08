# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockLotSaleOrderWizardLine(models.TransientModel):
    _name = "stock.lot.sale.order.wizard.line"
    _description = "Add Lot to Sale Order Wizard Line"

    wizard_id = fields.Many2one(
        "stock.lot.sale.order.wizard",
        string="Wizard",
        required=True,
    )
    lot_id = fields.Many2one(
        "stock.lot",
        string="Lot",
        required=True,
    )
    product_id = fields.Many2one(related="lot_id.product_id")
    quantity = fields.Float(string="Quantity")  # pylint: disable=W8113
    max_qty = fields.Float(string="Max Quantity", related="lot_id.product_qty")

    @api.constrains("quantity")
    def _check_quantity(self):
        """Check that the quantity is not greater than the max quantity."""
        for record in self:
            if record.quantity > record.max_qty:
                raise ValidationError(
                    _(
                        "The quantity of lot %(lot_name)s cannot be greater than "
                        "the available quantity %(max_qty)s.",
                        lot_name=record.lot_id.name,
                        max_qty=record.max_qty,
                    )
                )
