# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleCouponProgram(models.Model):
    """Extend to improve product related product management."""

    _inherit = "sale.coupon.program"

    force_product_default_code = fields.Char()
    # We would have "force_product_categ_id" required,
    # but to not break all unit tests on coupon programs on other modules,
    # we just add a required into the form view,
    # and do nothing in this code if not set.
    force_product_categ_id = fields.Many2one(
        comodel_name="product.category", domain=[("is_program_category", "=", True)],
    )
    discount_line_product_chosen = fields.Boolean()
    discount_line_product_readonly_id = fields.Many2one(
        related="discount_line_product_id", string="Reward Line Product Readonly",
    )

    @api.onchange("program_type", "promo_applicability")
    def _onchange_promo_applicability(self):
        if (
            self.program_type == "promotion_program"
            and self.promo_applicability == "on_next_order"
            and not self.force_product_categ_id
        ):
            # If several default categories found, just take the first
            default_categ = self.env["product.category"].search(
                [("default_promotion_next_order_category", "=", True)], limit=1
            )
            if default_categ:
                self.force_product_categ_id = default_categ.id

    @api.onchange("discount_line_product_chosen")
    def _onchange_discount_line_product_chosen(self):
        self.force_product_default_code = False
        if self.discount_line_product_id:
            self.discount_line_product_id = False

    @api.onchange("force_product_categ_id")
    def _onchange_force_product_categ_id(self):
        self.discount_line_product_id = False

    @api.constrains("force_product_categ_id", "reward_type", "discount_type")
    def _check_program_options(self):
        for rec in self:
            category = rec.force_product_categ_id
            if (
                category
                and category.program_product_discount_fixed_amount
                and not (
                    rec.reward_type == "discount"
                    and rec.discount_type == "fixed_amount"
                )
            ):
                raise UserError(
                    _(
                        "With 'program_product_discount_fixed_amount' category, "
                        "the reward type must be 'discount' and "
                        "the discount type must be 'Fixed Amount'."
                    )
                )

    def _check_no_product_duplicate(self):
        for rec in self.filtered("discount_line_product_id"):
            other_program_found = self.search_count(
                [
                    ("discount_line_product_id", "=", rec.discount_line_product_id.id),
                    ("id", "!=", rec.id),
                ]
            )
            if other_program_found:
                raise UserError(
                    _(
                        "This reward line product is already used "
                        "into another program."
                    )
                )

    def _force_values_on_product(self):
        product = self.discount_line_product_id
        # Check and force product category
        if product.categ_id != self.force_product_categ_id:
            product.categ_id = self.force_product_categ_id
        # Check and force product sale_ok code from category
        if product.sale_ok != product.categ_id.program_product_sale_ok:
            product.sale_ok = product.categ_id.program_product_sale_ok
        # Check and force product price from program
        if self.force_product_categ_id.program_product_discount_fixed_amount:
            product.lst_price = self.discount_fixed_amount
        if not self.discount_line_product_chosen:
            # Check and force product name from program
            if not self.discount_line_product_chosen:
                product.name = self.name
            # Check and force product default code from program
            if self.force_product_default_code:
                product.default_code = self.force_product_default_code

    def _create_custom_discount_line_product(self, name, category):
        values = {
            "name": name,
            "categ_id": category.id,
            "type": "service",
            "sale_ok": category.program_product_sale_ok,
            "purchase_ok": False,
            "invoice_policy": "order",
            "lst_price": 0,
        }
        return self.env["product.product"].create(values)

    @api.model
    def create(self, vals):
        if not vals.get("force_product_categ_id"):
            # Do nothing: we provides from unit tests or specific code
            return super().create(vals)
        if not vals.get("discount_line_product_id"):
            category = self.env["product.category"].browse(
                vals["force_product_categ_id"]
            )
            product = self._create_custom_discount_line_product(vals["name"], category)
            vals["discount_line_product_id"] = product.id
        program = super().create(vals)
        # Force values on generated product
        program._force_values_on_product()
        # Check we don't have a same product used on 2 programs
        program._check_no_product_duplicate()
        return program

    def write(self, vals):
        for program in self:
            if not program.force_product_categ_id and not vals.get(
                "force_product_categ_id"
            ):
                # Do nothing: we provides from unit tests or specific code
                super(SaleCouponProgram, program).write(vals)
                continue
            if vals.get(
                "discount_line_product_chosen", program.discount_line_product_chosen
            ):
                # Save the product name to restore it after core override
                if "discount_line_product_id" in vals:
                    product = self.env["product.product"].browse(
                        vals["discount_line_product_id"]
                    )
                    current_product_name = product.name
                else:
                    current_product_name = program.discount_line_product_id.name
            else:
                current_product_name = False
            # Call super to update program
            super(SaleCouponProgram, program).write(vals)
            # Create default product if missing and not chosen
            if not program.discount_line_product_chosen:
                if not program.discount_line_product_id:
                    product = self._create_custom_discount_line_product(
                        program.name, program.force_product_categ_id
                    )
                    program.discount_line_product_id = product
            # Restore original product name
            if (
                current_product_name
                and program.discount_line_product_id.name != current_product_name
            ):
                program.discount_line_product_id.name = current_product_name
            # Force values on generated product
            program._force_values_on_product()
            # Check we don't have a same product used on 2 programs
            program._check_no_product_duplicate()
        return True
