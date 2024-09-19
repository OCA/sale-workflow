# Copyright 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sale_ok = fields.Boolean(
        string="Can be added to Quote",
        copy=False,
        readonly=True,
    )
    sale_ok_confirm = fields.Boolean(
        string="Can be Sold",
        copy=False,
        readonly=True,
    )
    candidate_sale = fields.Boolean(
        string="Candidate to add to Quote",
        compute="_compute_candidate_sale_confirm",
        store=True,
        readonly=False,
    )
    candidate_sale_confirm = fields.Boolean(
        string="Candidate to be Sold",
        compute="_compute_candidate_sale_confirm",
        store=True,
        readonly=False,
    )
    can_edit_candidate = fields.Boolean(compute="_compute_can_edit_candidate")

    def _compute_can_edit_candidate(self):
        self.update(
            {
                "can_edit_candidate": self.env.user.has_group(
                    "sale_product_approval.group_product_administrator"
                )
            }
        )

    @api.depends("candidate_sale_confirm")
    def _compute_candidate_sale_confirm(self):
        for product in self:
            if product.candidate_sale_confirm:
                product.candidate_sale = True

    @api.model_create_multi
    def create(self, vals_list):
        templates = super().create(vals_list)
        templates._set_sale_ok_product()
        return templates

    def write(self, vals):
        res = super().write(vals)
        if (
            "product_state_id" in vals
            or "candidate_sale" in vals
            or "candidate_sale_confirm" in vals
        ):
            self._set_sale_ok_product()
        return res

    def _set_sale_ok_product(self):
        order_ids = (
            self.env["sale.order.line"]
            .search(
                [
                    ("product_id", "in", self.product_variant_ids.ids),
                    ("state", "in", ["draft", "sent"]),
                    ("approved_sale_confirm", "=", True),
                ]
            )
            .mapped("order_id")
        )
        for product in self:
            if product.product_state_id:
                product.sale_ok = (
                    product.candidate_sale and product.product_state_id.approved_sale
                )
                product.sale_ok_confirm = (
                    product.candidate_sale_confirm
                    and product.product_state_id.approved_sale_confirm
                )

                if not product.sale_ok_confirm:
                    order_ids._log_exception_activity_sale(product)

    @api.model
    def _get_default_product_state_id(self):
        return self.env.ref(
            "product_state.product_state_draft", raise_if_not_found=False
        )
