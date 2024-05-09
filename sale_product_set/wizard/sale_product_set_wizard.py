# Copyright 2015 Anybox S.A.S
# Copyright 2016-2020 Camptocamp SA
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, exceptions, fields, models


class SaleProductSetWizard(models.TransientModel):
    _inherit = "product.set.wizard"
    _name = "sale.product.set.wizard"
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
    skip_existing_products = fields.Boolean(
        default=False,
        help="Enable this to not add new lines "
        "for products already included in SO lines.",
    )

    @api.depends_context("product_set_add__set_line_ids")
    def _compute_product_set_line_ids(self):
        line_ids = self.env.context.get("product_set_add__set_line_ids", [])
        lines_from_ctx = self.env["product.set.line"].browse(line_ids)
        for rec in self:
            lines = lines_from_ctx.filtered(
                lambda x: x.product_set_id == rec.product_set_id
            )
            if lines:
                # Use the ones from ctx but make sure they belong to the same set.
                rec.product_set_line_ids = lines
            else:
                # Fallback to all lines from current set
                return super()._compute_product_set_line_ids()

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
        return super()._check_partner()

    def _allowed_order_partners(self):
        """Product sets' partners allowed for current sale order."""
        partner_ids = self.env.context.get("allowed_order_partner_ids")
        if partner_ids:
            return self.env["res.partner"].browse(partner_ids)
        return self.product_set_id.partner_id

    def add_set(self):
        """Add product set, multiplied by quantity in sale order line"""
        res = super().add_set()
        if not self.order_id:
            return res
        order_lines = self._prepare_order_lines()
        if order_lines:
            self.order_id.write({"order_line": order_lines})
        return order_lines

    def _prepare_order_lines(self):
        max_sequence = self._get_max_sequence()
        order_lines = []
        for seq, set_line in enumerate(self._get_lines(), start=1):
            values = self.prepare_sale_order_line_data(set_line)
            # When we play with sequence widget on a set of product,
            # it's possible to have a negative sequence.
            # In this case, the line is not added at the correct place.
            # So we have to force it with the order of the line.
            values.update({"sequence": max_sequence + seq})
            order_lines.append((0, 0, values))
        return order_lines

    def _get_max_sequence(self):
        max_sequence = 0
        if self.order_id.order_line:
            max_sequence = max(line.sequence for line in self.order_id.order_line)
        return max_sequence

    def _get_lines(self):
        if not self.order_id:
            yield from super()._get_lines()
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
        if set_line.display_type:
            line_values.update(
                {"name": set_line.name, "display_type": set_line.display_type}
            )

        return line_values
