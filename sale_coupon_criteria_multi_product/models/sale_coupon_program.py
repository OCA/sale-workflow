# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleCouponProgram(models.Model):
    _inherit = "sale.coupon.program"

    sale_coupon_criteria = fields.Selection(
        selection=[("domain", "Domain"), ("multi_product", "Multi Product")],
        string="Coupon criteria",
        help="- Domain: Standard behavior. The products are evaluated by domain.\n"
        "- Multi product: different rules can be applied to different products "
        "and all of the have to be fulfilled",
        default="domain",
    )
    sale_coupon_criteria_ids = fields.One2many(
        string="Multi Product Criterias",
        comodel_name="sale.coupon.criteria",
        inverse_name="program_id",
    )

    @api.onchange("sale_coupon_criteria")
    def _onchange_sale_coupon_criteria(self):
        """Clear domain so we clear some other fields from the view"""
        if self.sale_coupon_criteria == "multi_product":
            self.rule_products_domain = False

    def _filter_programs_on_products(self, order):
        """
        After splitting the programs according to their criteria, we'll check the rules
        on the multi-product ones to filter those that fulfill all the conditions.
        Depending on the Repeat Product setting a valid criteria will be:
        - Repeat: at least one of the products in the criteria and the minimum qty
        - No repeat: one unit every product in the criteria.
        All the criterias defined in a program must be fulfilled.
        """
        domain_programs = self.filtered(lambda x: x.sale_coupon_criteria == "domain")
        multi_product_programs = (self - domain_programs).filtered(
            "sale_coupon_criteria_ids"
        )
        # We'll return them altogether
        valid_domain_criteria_programs = super(
            SaleCouponProgram, domain_programs
        )._filter_programs_on_products(order)
        order_lines = (
            order.order_line.filtered(lambda line: line.product_id)
            - order._get_reward_lines()
        )
        products = order_lines.mapped("product_id")
        products_qties = dict.fromkeys(products, 0)
        for line in order_lines:
            products_qties[line.product_id] += line.product_uom_qty
        valid_multi_product_criteria_programs = multi_product_programs
        for program in multi_product_programs:
            criterias_are_valid = True
            for criteria in program.sale_coupon_criteria_ids:
                valid_products = program._get_valid_products_multi_product(
                    products, criteria
                )
                if not valid_products:
                    criterias_are_valid = False
                    break
                ordered_rule_products_qty = sum(
                    products_qties[p] for p in valid_products
                )
                # Avoid program if 1 ordered foo on a program '1 foo, 1 free foo'
                # as it's done in the standard
                if (
                    program.promo_applicability == "on_current_order"
                    and program.reward_type == "product"
                    and program.reward_product_id in criteria.product_ids
                ):
                    ordered_rule_products_qty -= program.reward_product_quantity
                if ordered_rule_products_qty < criteria.rule_min_quantity:
                    criterias_are_valid = False
                    break
            if not criterias_are_valid:
                valid_multi_product_criteria_programs -= program
        return valid_domain_criteria_programs + valid_multi_product_criteria_programs

    def _get_valid_products_multi_product(self, products, criteria):
        """Return valid products depending on the criteria repeat product setting. Then
        the main method will check if the minimum quantities are acomplished."""
        if criteria.repeat_product:
            return products.browse(
                [x.id for x in criteria.product_ids if x in products]
            )
        if not all([x in products for x in criteria.product_ids]):
            return self.env["product.product"]
        return criteria.product_ids
