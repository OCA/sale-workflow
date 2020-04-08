from odoo import _, api, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def get_move_from_line(self, line):
        move = self.env["stock.move"]
        # i create this counter to check lot's univocity on move line
        lot_count = 0
        for m in line.order_id.picking_ids.mapped("move_lines"):
            move_line_id = m.move_line_ids.filtered(lambda line: line.lot_id)
            if move_line_id and line.lot_id == move_line_id[0].lot_id:
                move = m
                lot_count += 1
                # if counter is 0 or > 1 means that something goes wrong
                if lot_count != 1:
                    raise UserError(_("Can't retrieve lot on stock"))
        return move

    @api.model
    def _check_move_state(self, line):
        if self.env.context.get("skip_check_lot_selection_move", False):
            return True
        if line.lot_id:
            move = self.get_move_from_line(line)
            if move.state == "confirmed":
                move._action_assign()
                move.refresh()
            if move.state != "assigned":
                raise UserError(
                    _("Can't reserve products for lot %s") % line.lot_id.name
                )
        return True

    def action_confirm(self):
        res = super(SaleOrder, self.with_context(sol_lot_id=True)).action_confirm()
        self._check_related_moves()
        return res

    def _check_related_moves(self):
        if self.env.context.get("skip_check_lot_selection_qty", False):
            return True
        for line in self.order_line:
            if line.lot_id:
                unreserved_moves = line.move_ids.filtered(
                    lambda move: move.product_uom_qty != move.reserved_availability
                )
                if unreserved_moves:
                    raise UserError(
                        _("Can't reserve products for lot %s") % line.lot_id.name
                    )
            self._check_move_state(line)
        return True
