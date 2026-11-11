# Copyright 2013-2014 Camptocamp SA - Guewen Baconnier
# © 2016 ForgeFlow, S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    warehouse_id = fields.Many2one(
        string="Default Warehouse",
        help="If no source warehouse is selected on line, "
        "this warehouse is used as default.",
    )

    show_sale_line_warehouse_column = fields.Boolean(
        related="company_id.show_sale_line_warehouse_column"
    )

    multiple_source_warehouses_message = fields.Char(
        compute="_compute_multiple_source_warehouses_message"
    )

    @api.depends(
        "order_line.warehouse_id",
        "order_line.display_type",
        "order_line.product_id.type",
    )
    def _compute_multiple_source_warehouses_message(self):
        for order in self:
            warehouses = order._get_source_warehouses()
            order.multiple_source_warehouses_message = (
                self.env._(
                    "The delivery is sent from multiple warehouses: %(warehouses)s",
                    warehouses=", ".join(sorted(warehouses.mapped("name"))),
                )
                if len(warehouses) > 1
                else False
            )

    def action_confirm(self):
        for order in self:
            warehouses = order._get_source_warehouses()
            if len(warehouses) == 1 and warehouses != order.warehouse_id:
                order.warehouse_id = warehouses
        return super().action_confirm()

    def _get_source_warehouses(self):
        """Return the warehouses of the lines that carry goods to deliver."""
        self.ensure_one()
        return self.order_line.filtered(
            lambda line: not line.display_type and line.product_id.type == "consu"
        ).warehouse_id


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    warehouse_id = fields.Many2one(
        inverse="_inverse_warehouse_id",
        readonly=False,
        check_company=True,
    )
    is_warehouse_id_following_order = fields.Boolean(
        default=True,
        help="True while the line warehouse follows the order warehouse.",
    )

    @api.depends(
        "route_id", "order_id.warehouse_id", "product_packaging_id", "product_id"
    )
    def _compute_warehouse_id(self):
        # Only recompute lines still following the order.
        lines = self.filtered("is_warehouse_id_following_order")
        return super(SaleOrderLine, lines)._compute_warehouse_id()

    def _inverse_warehouse_id(self):
        # Store "follows the order" at line write time. Needed because on an
        # order warehouse change the compute would compare old line vs new order.
        for line in self:
            line.is_warehouse_id_following_order = (
                not line.warehouse_id or line.warehouse_id == line.order_id.warehouse_id
            )

    def _prepare_procurement_group_vals(self):
        vals = super()._prepare_procurement_group_vals()
        # for compatibility with sale_quotation_sourcing
        if self._get_procurement_group_key()[0] == 10:
            if self.warehouse_id:
                vals["name"] += "/" + self.warehouse_id.name
        return vals

    def _get_procurement_group_key(self):
        """Return a key with priority to be used to regroup lines in multiple
        procurement groups

        """
        priority = 10
        key = super()._get_procurement_group_key()
        # Check priority
        if key[0] >= priority:
            return key
        wh_id = (
            self.warehouse_id.id if self.warehouse_id else self.order_id.warehouse_id.id
        )
        return priority, wh_id
