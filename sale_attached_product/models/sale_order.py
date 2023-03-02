# Copyright 2022 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "sale.attached.product.mixin"]

    @api.model
    def _get_auto_refresh_attached_product_triggers(self) -> set:
        """Normally, we won't be needing any field from sale.order but order lines
        but it's configurable anyway."""
        triggers = super()._get_auto_refresh_attached_product_triggers()
        order_line_triggers = (
            self.order_line._get_auto_refresh_attached_product_triggers()
        )
        for trigger in order_line_triggers:
            triggers.update({"order_line.{}".format(trigger)})
        return triggers

    def _get_attached_line_values_product(self, line, product):
        """Prepare the values for the attached line. This is used for creating or
        updating."""

        def _execute_onchanges(records, field_name):
            """Helper methods that executes all onchanges associated to a field."""
            for onchange in records._onchange_methods.get(field_name, []):
                for record in records:
                    onchange(record)

        # We prepare a new line and trigger the proper onchanges to ensure we get the
        # right line values (price unit according to the customer pricelist, taxes, ect)
        order_line = self.order_line.new(
            {"order_id": self.id, "product_id": product.id}
        )
        _execute_onchanges(order_line, "product_id")
        order_line.update({"product_uom_qty": line.product_uom_qty})
        _execute_onchanges(order_line, "product_uom_qty")
        vals = order_line._convert_to_write(order_line._cache)
        vals.update({"is_attached_line": True, "attached_from_line_id": line.id})
        return vals

    def _create_attached_line(self, lines):
        """We create all the lines at once. This should be more performant"""
        vals_list = []
        for line in lines:
            for product in line._get_attached_products():
                vals_list.append(self._get_attached_line_values_product(line, product))
        if vals_list:
            self.with_context(skip_auto_refresh_attached_product=True).write(
                {"order_line": [(0, False, value) for value in vals_list]}
            )

    def _cleanup_attached_lines(self):
        """Remove those line which main line is already removed or wich main line
        product attachment won't match its lines."""
        self.ensure_one()
        auto_update_attached_lines = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_attached_product.auto_update_attached_lines")
        )
        lines = self.order_line.filtered("is_attached_line")
        lines.filtered(lambda x: not x.attached_from_line_id).unlink()
        if not auto_update_attached_lines:
            return
        # We also want to remove those lines which main product doesn't match anymore
        # but only when auto update is on
        lines_with_attachements = self.order_line.filtered("attached_line_ids")
        for line in lines_with_attachements:
            attached_products = line._get_attached_products()
            line.attached_line_ids.with_context(
                skip_auto_refresh_attached_product=True
            ).filtered(lambda x: x.product_id not in attached_products).unlink()

    def _create_attached_lines(self):
        """New attached lines. After this, they'll be updated if there are changes in
        the main line."""
        self.ensure_one()
        self._create_attached_line(
            self.order_line.filtered(
                lambda x: not x.attached_line_ids and x._get_attached_products()
            )
        )

    def _update_attached_lines(self):
        """Update attached lines values related to their main line."""
        self.ensure_one()
        lines_with_attachements = self.order_line.filtered("attached_line_ids")
        lines_to_remove = self.env["sale.order.line"]
        missing_list = []
        for line in lines_with_attachements:
            # Lines with no qty can be considered to be removed.
            if not line.product_uom_qty:
                lines_to_remove += line.attached_line_ids
                continue
            # For every unit of the main line there will another of the attached one
            attached_line_qtys = set(line.attached_line_ids.mapped("product_uom_qty"))
            if any(q != line.product_uom_qty for q in attached_line_qtys):
                line.attached_line_ids.update({"product_uom_qty": line.product_uom_qty})
                # Trigger possible pricelist changes
                for attached_line in line.attached_line_ids:
                    attached_line.product_uom_change()
            attached_products = line._get_attached_products()
            # Create missing products, for example in the case of a deleted attached
            # line.
            missing_products = {
                p
                for p in attached_products
                if p not in line.attached_line_ids.product_id
            }
            for product in missing_products:
                missing_list.append(
                    self._get_attached_line_values_product(line, product)
                )
        lines_to_remove.with_context(skip_auto_refresh_attached_product=True).unlink()
        self.with_context(skip_auto_refresh_attached_product=True).write(
            {"order_line": [(0, False, value) for value in missing_list]}
        )

    def recompute_attached_products(self):
        """Recurrent method for recomputing attached lines. Always done in these three
        steps:

        1. A cleanup of orphaned attached lines or attached lines that doesn't match
           their parent attached products anymore.
        2. Creating new attached lines from lines which don't have them.
        3. Updating existing attached lines. Mainly for quantity"""
        auto_update_attached_lines = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_attached_product.auto_update_attached_lines")
        )
        for order in self.filtered(lambda x: x.state not in {"done", "cancel"}):
            order._cleanup_attached_lines()
            order._create_attached_lines()
            auto_update_attached_lines and order._update_attached_lines()

    @api.model_create_multi
    def create(self, vals_list):
        if self._check_skip_attached_product_refresh():
            return super().create(vals_list)
        orders = super().create(vals_list)
        orders.recompute_attached_products()
        return orders

    def write(self, vals):
        if self._check_skip_attached_product_refresh():
            return super().write(vals)
        old_data = self._get_recs_data()
        self_ctx = self.with_context(skip_auto_refresh_attached_product=True)
        res = super(SaleOrder, self_ctx).write(vals)
        new_data = self._get_recs_data()
        if old_data != new_data:
            self.recompute_attached_products()
        return res


class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = ["sale.order.line", "sale.attached.product.mixin"]

    is_attached_line = fields.Boolean(
        help="Flag products that are attached to their main counterpart"
    )
    attached_from_line_id = fields.Many2one(comodel_name="sale.order.line")
    attached_line_ids = fields.One2many(
        comodel_name="sale.order.line",
        inverse_name="attached_from_line_id",
    )

    def _get_attached_products(self):
        return self.product_id.product_tmpl_id.attached_product_ids.filtered(
            lambda x: not x.company_id or x.company_id == self.company_id
        )

    @api.model_create_multi
    def create(self, vals_list):
        if self._check_skip_attached_product_refresh():
            return super().create(vals_list)
        self_ctx = self.with_context(skip_auto_refresh_attached_product=True)
        lines = super(SaleOrderLine, self_ctx).create(vals_list)
        lines.mapped("order_id").recompute_attached_products()
        return lines

    def write(self, vals):
        if self._check_skip_attached_product_refresh():
            return super().write(vals)
        old_data = self._get_recs_data()
        old_orders = self.mapped("order_id")
        self_ctx = self.with_context(skip_auto_refresh_attached_product=True)
        res = super(SaleOrderLine, self_ctx).write(vals)
        new_data = self._get_recs_data()
        new_orders = self.mapped("order_id")
        if old_data != new_data:
            (old_orders | new_orders).recompute_attached_products()
        return res

    def unlink(self):
        if self._check_skip_attached_product_refresh():
            return super().unlink()
        orders = self.mapped("order_id")
        self_ctx = self.with_context(skip_auto_refresh_attached_product=True)
        res = super(SaleOrderLine, self_ctx).unlink()
        orders.recompute_attached_products()
        return res

    @api.model
    def _get_auto_refresh_attached_product_triggers(self) -> set:
        triggers = super()._get_auto_refresh_attached_product_triggers()
        triggers.update({"product_id", "product_uom", "product_uom_qty"})
        return triggers
