# Copyright 2025 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    semaphore_active = fields.Boolean(
        compute="_compute_semaphore_values",
        inverse="_inverse_semaphore_active",
    )
    semaphore_discount_success = fields.Float(
        string="Discount Success",
        compute="_compute_semaphore_values",
        inverse="_inverse_semaphore_discount_success",
    )
    semaphore_discount_warning = fields.Float(
        string="Discount Warning",
        compute="_compute_semaphore_values",
        inverse="_inverse_semaphore_discount_warning",
    )
    semaphore_discount_danger = fields.Float(
        string="Discount Danger",
        compute="_compute_semaphore_values",
        inverse="_inverse_semaphore_discount_danger",
    )

    @api.depends(
        "product_variant_ids",
        "product_variant_ids.semaphore_active",
        "product_variant_ids.semaphore_discount_success",
        "product_variant_ids.semaphore_discount_warning",
        "product_variant_ids.semaphore_discount_danger",
    )
    def _compute_semaphore_values(self):
        self.semaphore_active = False
        self.semaphore_discount_success = 0
        self.semaphore_discount_warning = 0
        self.semaphore_discount_danger = 0
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1
        )
        for template in unique_variants:
            template.semaphore_active = template.product_variant_ids.semaphore_active
            template.semaphore_discount_success = (
                template.product_variant_ids.semaphore_discount_success
            )
            template.semaphore_discount_warning = (
                template.product_variant_ids.semaphore_discount_warning
            )
            template.semaphore_discount_danger = (
                template.product_variant_ids.semaphore_discount_danger
            )

    def _inverse_semaphore_active(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.semaphore_active = (
                    template.semaphore_active
                )

    def _inverse_semaphore_discount_success(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.semaphore_discount_success = (
                    template.semaphore_discount_success
                )

    def _inverse_semaphore_discount_warning(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.semaphore_discount_warning = (
                    template.semaphore_discount_warning
                )

    def _inverse_semaphore_discount_danger(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.semaphore_discount_danger = (
                    template.semaphore_discount_danger
                )


class ProductProduct(models.Model):
    _inherit = "product.product"

    semaphore_active = fields.Boolean()
    semaphore_discount_success = fields.Float(string="Discount Success")
    semaphore_discount_warning = fields.Float(string="Discount Warning")
    semaphore_discount_danger = fields.Float(string="Discount Danger")

    def _get_semaphore_data(self):
        if not self.semaphore_active and not self.categ_id.semaphore_active:
            return False
        record = self if self.semaphore_active else self.categ_id
        return {
            "success": record.semaphore_discount_success,
            "warning": record.semaphore_discount_warning,
            "danger": record.semaphore_discount_danger,
        }
