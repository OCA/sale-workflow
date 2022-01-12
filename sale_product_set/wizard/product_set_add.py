# Copyright 2015 Anybox S.A.S
# Copyright 2016-2020 Camptocamp SA
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, exceptions, fields, models


class ProductSetAdd(models.TransientModel):
    _name = "product.set.add"
    _rec_name = "product_set_id"
    _description = "Wizard model to add product set into a quotation"

    order_id = fields.Many2one(
        "sale.order",
        "Sale Order",
        required=True,
        default=lambda self: self.env.context.get("active_id")
        if self.env.context.get("active_model") == "sale.order"
        else None,
        ondelete="cascade",
    )
    partner_id = fields.Many2one(related="order_id.partner_id", ondelete="cascade")
    product_set_id = fields.Many2one(
        "product.set", "Product set", required=True, ondelete="cascade"
    )
    product_set_line_ids = fields.Many2many(
        "product.set.line",
        string="Product set lines",
        required=True,
        store=True,
        ondelete="cascade",
        compute="_compute_product_set_line_ids",
        readonly=False,
    )
    quantity = fields.Float(
        digits="Product Unit of Measure", required=True, default=1.0
    )
    skip_existing_products = fields.Boolean(
        default=False,
        help="Enable this to not add new lines "
        "for products already included in SO lines.",
    )

    @api.depends_context("product_set_add__set_line_ids")
    @api.depends("product_set_id")
    def _compute_product_set_line_ids(self):
        line_ids = self.env.context.get("product_set_add__set_line_ids", [])
        lines_from_ctx = self.env["product.set.line"].browse(line_ids)
        for rec in self:
            if rec.product_set_line_ids:
                # Passed on creation
                continue
            lines = lines_from_ctx.filtered(
                lambda x: x.product_set_id == rec.product_set_id
            )
            if lines:
                # Use the ones from ctx but make sure they belong to the same set.
                rec.product_set_line_ids = lines
            else:
                # Fallback to all lines from current set
                rec.product_set_line_ids = rec.product_set_id.set_line_ids

    def _check_partner(self):
        """Validate order partner against product set's partner if any."""
        if not self.product_set_id.partner_id or self.env.context.get(
            "product_set_add_skip_validation"
        ):
            return

        allowed_partners = self._allowed_order_partners()
        if self.order_id.partner_id not in allowed_partners:
            raise exceptions.ValidationError(
                _(
                    "You can use a sale order assigned "
                    "only to following partner(s): {}"
                ).format(", ".join(allowed_partners.mapped("name")))
            )

    def _allowed_order_partners(self):
        """Product sets' partners allowed for current sale order."""
        partner_ids = self.env.context.get("allowed_order_partner_ids")
        if partner_ids:
            return self.env["res.partner"].browse(partner_ids)
        return self.product_set_id.partner_id

    def add_set(self):
        """Add product set, multiplied by quantity in sale order line"""
        self._check_partner()
        order_lines = self._prepare_order_lines()
        if order_lines:
            self.order_id.write({"order_line": order_lines})
        return order_lines

    def _prepare_order_lines(self):
        max_sequence = self._get_max_sequence()
        order_lines = []
        for set_line in self._get_lines():
            order_lines.append(
                (
                    0,
                    0,
                    self.prepare_sale_order_line_data(
                        set_line, max_sequence=max_sequence
                    ),
                )
            )
        return order_lines

    def _get_max_sequence(self):
        max_sequence = 0
        if self.order_id.order_line:
            max_sequence = max([line.sequence for line in self.order_id.order_line])
        return max_sequence

    def _get_lines(self):
        # hook here to take control on used lines
        so_product_ids = self.order_id.order_line.mapped("product_id").ids
        for set_line in self.product_set_line_ids:
            if self.skip_existing_products and set_line.product_id.id in so_product_ids:
                continue
            yield set_line

    def prepare_sale_order_line_data(self, set_line, max_sequence=0):
        self.ensure_one()
        line_values = set_line.prepare_sale_order_line_values(
            self.order_id, self.quantity, max_sequence=max_sequence
        )
        sol_model = self.env["sale.order.line"]
        line_values.update(sol_model.play_onchanges(line_values, line_values.keys()))
        return line_values
