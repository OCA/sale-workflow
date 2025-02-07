# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    stock_is_reserved = fields.Boolean(
        compute="_compute_stock_is_reserved",
        store=True,
    )

    def _get_reservation_pickings(self):
        return self.picking_ids.filtered(
            lambda p: any(m.used_for_sale_reservation for m in p.move_ids)
        )

    @api.depends("picking_ids.move_ids.used_for_sale_reservation")
    def _compute_stock_is_reserved(self):
        for rec in self:
            rec.stock_is_reserved = (rec._get_reservation_pickings() and True) or False

    def _action_cancel(self):
        self.release_reservation()
        return super()._action_cancel()

    def _action_confirm(self):
        self.release_reservation()
        return super()._action_confirm()

    def _prepare_reserve_procurement_group_values(self):
        self.ensure_one()
        line = fields.first(self.order_line)
        values = line._prepare_procurement_group_vals()
        values["name"] = f"Reservation for {values['name']}"
        return values

    def _create_reserve_procurement_group(self):
        return self.env["procurement.group"].create(
            self._prepare_reserve_procurement_group_values()
        )

    def reserve_stock(self):
        self = self.filtered(
            lambda s: not s.stock_is_reserved
            and s.state in ["draft", "sent"]
            or not s.order_line
        )
        if not self:
            return

        self = self.with_context(sale_stock_prebook_stop_proc_run=True)
        procurements = []

        for order in self:
            group = order._create_reserve_procurement_group()
            procurements += order.order_line._prepare_reserve_procurements(group)
        if procurements:
            self.env["procurement.group"].run(procurements)

    def release_reservation(self):
        pickings = self._get_reservation_pickings()
        pickings.action_cancel()
        pickings.group_id.sudo().unlink()
        pickings.sudo().unlink()
