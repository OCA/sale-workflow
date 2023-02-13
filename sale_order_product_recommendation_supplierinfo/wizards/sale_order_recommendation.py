# Copyright 2019 David Vidal <david.vidal@tecnativa.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderRecommendation(models.TransientModel):
    _inherit = "sale.order.recommendation"

    origin_recommendation = fields.Selection(
        selection_add=[("supplierinfo", "Vendor pricelists")],
        ondelete={"origin_recommendation": "set sale_order"},
    )

    def _get_supplierinfo_comment(self):
        if "comment" in self.env["product.supplierinfo"]._fields:
            return "comment"
        return "product_name"

    def _get_origin_recommendation_supplierinfo(self):
        today = fields.Date.context_today(self)
        products = self._get_allowed_products()
        domain = [
            "&",
            "|",
            ("product_id", "in", products.ids),
            ("product_tmpl_id", "in", products.product_tmpl_id.ids),
            "&",
            "|",
            ("date_start", "=", False),
            ("date_start", "<=", today),
            "|",
            ("date_end", "=", False),
            ("date_end", ">=", today),
        ]
        supplierinfos = self.env["product.supplierinfo"].search(domain)
        return [
            {
                "product_id": (
                    ln.product_id.id or ln.product_tmpl_id.product_variant_id.id,
                    ln.product_id.name or ln.product_tmpl_id.product_variant_id.name,
                ),
                "vendor_id": (ln.name.id, ln.name.name),
                "comment": ln[self._get_supplierinfo_comment()],
            }
            for ln in supplierinfos
        ]

    def _prepare_recommendation_line_vals(self, group_line, so_line=False):
        vals = super()._prepare_recommendation_line_vals(group_line, so_line=so_line)
        if group_line.get("vendor_id", False):
            vals["vendor_id"] = group_line["vendor_id"][0]
        if group_line.get("comment", False):
            vals["vendor_comment"] = group_line["comment"]
        return vals


class SaleOrderRecommendationLine(models.TransientModel):
    _inherit = "sale.order.recommendation.line"

    vendor_id = fields.Many2one(comodel_name="res.partner", readonly=True)
    vendor_comment = fields.Char(readonly=True)

    def _prepare_update_so_line(self, line_form):
        res = super()._prepare_update_so_line(line_form)
        if self.vendor_comment and self.vendor_comment not in line_form.name:
            line_form.name += self.vendor_comment
        return res

    def _prepare_new_so_line(self, line_form, sequence):
        res = super()._prepare_new_so_line(line_form, sequence)
        if self.vendor_comment:
            line_form.name += self.vendor_comment
        return res
