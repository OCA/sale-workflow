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
        if self._context.get("sol_lot_id"):
            lot_id = self.sale_line_id.lot_id
        return super(StockMove, self)._update_reserved_quantity(
            need,
            available_quantity,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        vals = super(StockMove, self)._prepare_move_line_vals(
            quantity=quantity, reserved_quant=reserved_quant
        )
        if reserved_quant and self.sale_line_id:
            vals["lot_id"] = self.sale_line_id.lot_id.id
        return vals
