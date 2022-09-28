# Copyright 2018 Tecnativa - Sergio Teruel
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


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
    _inherit = "sale.order.line"

    elaboration_id = fields.Many2one(
        comodel_name="product.elaboration", string="Elaboration", ondelete="restrict"
    )
    elaboration_note = fields.Char(
        string="Elaboration Note",
        store=True,
        compute="_compute_elaboration_note",
        readonly=False,
    )
    is_elaboration = fields.Boolean(
        string="Is Elaboration",
        store=True,
        compute="_compute_is_elaboration",
        readonly=False,
    )
    date_order = fields.Datetime(related="order_id.date_order", string="Date")

    @api.depends("elaboration_id")
    def _compute_elaboration_note(self):
        for line in self:
            line.elaboration_note = line.elaboration_id.name

    def _prepare_invoice_line(self, **optional_values):
        vals = super()._prepare_invoice_line(**optional_values)
        if self.is_elaboration:
            vals["name"] = "{} - {}".format(self.order_id.name, self.name)
        return vals

    @api.depends("product_id")
    def _compute_is_elaboration(self):
        """We use computed instead of a related field because related fields are not
        initialized with their value on one2many which related field is the
        inverse_name, so with this we get immediately the value on NewIds.
        """
        for line in self:
            line.is_elaboration = line.product_id.is_elaboration
