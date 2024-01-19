# Copyright 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class SaleOrderOption(models.Model):
    _inherit = "sale.order.option"

    quantity = fields.Float(
        compute="_compute_quantity",
        readonly=False,
        store=True,
    )

    @api.model
    def _get_create_ignore_fields(self):
        """
        Override this method in your module to
        add or remove (more likely remove) fields
        from the list of fields to ignore on creation.

        In case of this module we need to prevent quantity field
        from being set by product configurator when we're trying
        to create an option.

        Returns:
            list: list of fields to ignore on creation
        """
        return ["quantity"]

    @api.model_create_multi
    def create(self, vals_list):
        """
        Remove quantity field on option creation to trigger
        desired behaviour of quantity computation.

        See '_get_create_ignore_fields' method docstring
        for more info.
        """
        for vals in vals_list:
            for field_ in self._get_create_ignore_fields():
                if field_ in vals:
                    del vals[field_]
        return super().create(vals_list)

    @api.depends("order_id.order_line")
    def _compute_quantity(self):
        """
        Compute quantity based on optional product
        quantities configured in product templates
        from lines of Quotation/Sale Order.
        """
        for option in self:
            order = option.order_id
            option_product_id = option.product_id.product_tmpl_id.id
            order_lines = order.order_line.filtered(
                lambda x: option_product_id
                in (x.product_template_id.optional_product_ids.ids)
            )
            if not order_lines:
                option.quantity = 1
                continue

            multiplier = sum(
                order_lines.mapped("product_template_id")
                .mapped("product_optional_line_ids")
                .mapped("quantity")
            )
            qty = sum(order_lines.mapped("product_uom_qty"))
            option.quantity = qty * multiplier
