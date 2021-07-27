from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _update_reserved_quantity(
        self,
        need,
        available_quantity,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=True,
    ):
        if (
            self.sale_line_id.lot_id
            and available_quantity >= self.sale_line_id.product_uom_qty
        ):
            lot_id = self.sale_line_id.lot_id
        return super()._update_reserved_quantity(
            need,
            available_quantity,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        vals = super()._prepare_move_line_vals(
            quantity=quantity, reserved_quant=reserved_quant
        )
        lot = self.sale_line_id.lot_id
        if (
            reserved_quant
            and reserved_quant.lot_id
            and lot
            and reserved_quant.lot_id == lot
        ):
            vals["lot_id"] = lot.id
        return vals
