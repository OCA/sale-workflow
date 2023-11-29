# Copyright 2018 Tecnativa - Sergio Teruel
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


def _execute_onchanges(records, field_name):
    """Helper methods that executes all onchanges associated to a field."""
    for onchange in records._onchange_methods.get(field_name, []):
        for record in records:
            onchange(record)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _create_elaboration_line(self, product, qty):
        """Create a sale order line from a elaboration product, search a line
        with the same elaboration product to add qty
        :param product:
        :param qty:
        :return: the sale order line record created
        """
        SaleOrderLine = self.env["sale.order.line"]
        sol_for_product = self.order_line.filtered(lambda x: x.product_id == product)[
            :1
        ]
        if sol_for_product:
            sol_for_product.product_uom_qty += qty
            return sol_for_product
        sol = SaleOrderLine.new(
            {"order_id": self.id, "product_id": product.id, "is_elaboration": True}
        )
        _execute_onchanges(sol, "product_id")
        sol.update({"product_uom_qty": qty})
        _execute_onchanges(sol, "product_uom_qty")
        vals = sol._convert_to_write(sol._cache)
        if self.order_line:
            vals["sequence"] = self.order_line[-1].sequence + 1
        return SaleOrderLine.sudo().create(vals)


class SaleOrderLine(models.Model):
    _inherit = ["sale.order.line", "product.elaboration.mixin"]
    _name = "sale.order.line"

    date_order = fields.Datetime(related="order_id.date_order", string="Date")
    route_id = fields.Many2one(compute="_compute_route_id", store=True, readonly=False)
    elaboration_profile_id = fields.Many2one(
        related="product_id.elaboration_profile_id"
    )
    elaboration_price_unit = fields.Float(
        "Elab. Price", compute="_compute_elaboration_price_unit", store=True
    )
    is_prepared = fields.Boolean(
        compute=lambda self: None,
        search="_search_is_prepared",
        help=("Dummy field to be able to find prepared lines"),
    )

    def get_elaboration_stock_route(self):
        self.ensure_one()
        return self.elaboration_ids.route_ids[:1]

    @api.depends("elaboration_ids")
    def _compute_route_id(self):
        for line in self:
            route_id = line.get_elaboration_stock_route()
            if route_id:
                line.route_id = route_id

    @api.depends("elaboration_ids", "order_id.pricelist_id")
    def _compute_elaboration_price_unit(self):
        for line in self:
            if not line.order_id.pricelist_id:
                line.elaboration_price_unit = 0
            else:
                line.elaboration_price_unit = sum(
                    line.order_id.pricelist_id._get_products_price(
                        line.elaboration_ids.product_id,
                        quantity=1,
                    ).values()
                )

    def _prepare_invoice_line(self, **optional_values):
        vals = super()._prepare_invoice_line(**optional_values)
        if self.is_elaboration:
            vals["name"] = "{} - {}".format(self.order_id.name, self.name)
        return vals

    def _search_is_prepared(self, operator, value):
        if operator != "=":
            raise UserError(
                _("Unsupported operator %s for searching on is_prepared") % (operator,)
            )
        moves = self.env["stock.move"].search(
            [
                (
                    "state",
                    "not in" if value else "in",
                    [
                        "draft",
                        "waiting",
                        "confirmed",
                        "partially_available",
                        "assigned",
                    ],
                ),
                (
                    "location_dest_id",
                    "=",
                    self.env.ref("stock.stock_location_customers").id,
                ),
            ]
        )
        return [("move_ids", "in", moves.ids)]
