# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_reserve_procurement_values(self, group_id=None):
        values = self._prepare_procurement_values(group_id)
        values["used_for_sale_reservation"] = True
        return values

    def _should_prebook_stock(self):
        """Checks if SOL product has no_sale_stock_prebook set
        to know if we need to reserve it or not"""
        self.ensure_one()
        for route in self.product_id.route_ids:
            if route.no_sale_stock_prebook:
                return False
        return True

    def _prepare_reserve_procurement(self, group):
        """Adjusts UOM qty for product, makes list of field values for
        procurement group"""
        product_qty, procurement_uom = self.product_uom._adjust_uom_quantities(
            self.product_uom_qty, self.product_id.uom_id
        )
        return self.env["procurement.group"].Procurement(
            self.product_id,
            product_qty,
            procurement_uom,
            self.order_id.partner_shipping_id.property_stock_customer,
            self.product_id.display_name,
            group.name,
            self.order_id.company_id,
            self._prepare_reserve_procurement_values(group_id=group),
        )

    def _prepare_reserve_procurements(self, group):
        """Prepares list of dicts - reserve procurements"""
        procurements = []
        for line in self:
            if not line._should_prebook_stock():
                continue
            procurements.append(line._prepare_reserve_procurement(group))
        return procurements


class SaleOrder(models.Model):
    _inherit = "sale.order"

    stock_is_reserved = fields.Boolean(
        "Stock is reserved",
        compute="_compute_stock_is_reserved",
        store=True,
    )

    def _get_reservation_pickings(self):
        return self.picking_ids.filtered(
            lambda p: any(m.used_for_sale_reservation for m in p.move_lines)
        )

    @api.depends("picking_ids.move_lines.used_for_sale_reservation")
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
        values = self.order_line[0]._prepare_procurement_group_vals()
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
