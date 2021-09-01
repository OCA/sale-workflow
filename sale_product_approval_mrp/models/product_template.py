# Copyright 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    mrp_ok = fields.Boolean(
        string="Can be Manufactured",
        copy=False,
        readonly=True,
    )
    mrp_component_ok = fields.Boolean(
        string="Can be a Component on a Manufacturing Order",
        copy=False,
        readonly=True,
    )
    bom_ok = fields.Boolean(
        string="Can be on BoM",
        copy=False,
        readonly=True,
    )
    candidate_manufacture = fields.Boolean(string="Candidate to be Manufactured")
    candidate_component_manufacture = fields.Boolean(
        string="Candidate to be a Component on Manufacturing Orders"
    )
    candidate_bom = fields.Boolean(string="Candidate to be on BoM")

    @api.model
    def create(self, vals):
        new = super().create(vals)
        new._set_mrp_ok()
        new._set_mrp_component_ok()
        new._set_bom_ok()
        return new

    def write(self, vals):
        res = super().write(vals)
        if "product_state_id" in vals:
            to_state = self.product_state_id.code
            to_state != "draft" and (
                self._set_mrp_ok() or self._set_mrp_component_ok() or self._set_bom_ok()
            )
        return res

    def _set_mrp_ok(self):
        for product in self:
            if product.product_state_id:
                product.mrp_ok = (
                    product.candidate_manufacture
                    and product.product_state_id.approved_mrp
                )
                if not product.mrp_ok:
                    order_ids = self.env["mrp.production"].search(
                        [
                            ("product_id", "in", product.product_variant_ids.ids),
                            ("state", "in", ["draft", "confirmed", "progress"]),
                            ("mo_exceptions", "=", True),
                        ]
                    )
                    order_ids._log_exception_activity_mrp(product)

    def _set_mrp_component_ok(self):
        for product in self:
            if product.product_state_id:
                product.mrp_component_ok = (
                    product.candidate_component_manufacture
                    and product.product_state_id.approved_component_mrp
                )
                if not product.mrp_component_ok:
                    order_ids = (
                        self.env["stock.move"]
                        .search(
                            [
                                ("product_id", "in", product.product_variant_ids.ids),
                                (
                                    "raw_material_production_id.state",
                                    "in",
                                    ["draft", "confirmed", "progress"],
                                ),
                                ("approved_mrp_component_ok", "=", True),
                            ]
                        )
                        .mapped("raw_material_production_id")
                    )
                    order_ids._log_exception_activity_mrp(product)

    def _set_bom_ok(self):
        for product in self:
            if product.product_state_id:
                product.bom_ok = (
                    product.candidate_bom and product.product_state_id.approved_bom
                )
