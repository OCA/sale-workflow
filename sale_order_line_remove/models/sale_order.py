# Copyright 2023 ForgeFlow, S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _check_line_unlink(self):
        non_removable_lines = super(SaleOrderLine, self)._check_line_unlink()
        removable_lines = self.filtered(
            lambda line: line.state in ("sale", "done")
            and not line.invoice_lines
            and not line.move_ids.filtered(lambda move: move.state == "done")
        )
        invoiced_lines = self.sudo().filtered(
            lambda line: line.state in ("sale", "done") and line.invoice_lines
        )
        if invoiced_lines:
            raise UserError(
                _("You can not remove an order line that has been invoiced")
            )
        delivered_lines = self.sudo().filtered(
            lambda line: line.state in ("sale", "done")
            and line.move_ids.filtered(lambda move: move.state == "done")
        )
        if delivered_lines:
            raise UserError(
                _("You can not remove an order line that has been delivered")
            )
        return non_removable_lines - removable_lines

    def unlink(self):
        non_removable_lines = self._check_line_unlink()
        for line in self - non_removable_lines:
            related_pickings = line.move_ids.mapped("picking_id")
            line.move_ids.filtered(
                lambda move: move.state not in ("done", "cancel")
            )._action_cancel()
            line.move_ids.filtered(lambda move: move.state != "done").unlink()
            for picking in related_pickings:
                if not picking.move_ids_without_package:
                    picking.unlink()
        return super(SaleOrderLine, self).unlink()
