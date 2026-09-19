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
        "this warehouse is used as default. ",
    )


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    warehouse_id = fields.Many2one(readonly=False)

    @api.depends("route_ids", "order_id.warehouse_id", "product_id")
    def _compute_warehouse_id(self):
        """compute the warehouse for the lines only
        if it has not already been set."""
        lines = self.filtered(lambda rec: not rec.warehouse_id)
        return super(SaleOrderLine, lines)._compute_warehouse_id()

    def _get_stock_reference_key(self):
        """Return a key with priority to be used to regroup lines in multiple
        stock references, so that lines sourced from different warehouses are
        not grouped together.
        """
        priority = 10
        key = super()._get_stock_reference_key()
        # Check priority
        if key[0] >= priority:
            return key
        wh_id = (
            self.warehouse_id.id if self.warehouse_id else self.order_id.warehouse_id.id
        )
        return priority, wh_id

    def _prepare_reference_vals(self):
        vals = super()._prepare_reference_vals()
        # for compatibility with sale_quotation_sourcing
        if self._get_stock_reference_key()[0] == 10 and self.warehouse_id:
            vals["name"] += "/" + self.warehouse_id.name
        return vals
