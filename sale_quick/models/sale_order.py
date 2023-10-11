# Copyright 2022 Camptocamp SA
# @author: Damien Crier <damien.crier@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "product.mass.addition"]

    def _get_context_add_products(self):
        res = {
            "search_default_filter_to_sale": 1,
            "quick_access_rights_sale": 1,
        }
        # Lazy dependency with sale_stock
        if "warehouse_id" in self._fields:
            res.update(
                {
                    "warehouse": self.warehouse_id.id,
                    "to_date": self.commitment_date,
                }
            )
        return res

    def _get_domain_add_products(self):
        field = self.env["sale.order.line"]._fields.get("product_id")
        return safe_eval(field.domain, {"company_id": self.company_id.id})

    def add_product(self):
        self.ensure_one()
        res = self._common_action_keys()
        res["context"].update(self._get_context_add_products())
        domain = self._get_domain_add_products()
        if domain:
            res["domain"] = domain
        commercial = self.partner_id.commercial_partner_id.name
        res["name"] = "🔙 {} ({})".format(_("Product Variants"), commercial)
        res["view_id"] = (self.env.ref("sale_quick.product_tree_view4sale").id,)
        return res

    def _get_quick_line(self, product):
        result = self.order_line.filtered(lambda rec: rec.product_id == product)

        nr_lines = len(result.ids)
        if nr_lines > 1:
            raise ValidationError(
                _(
                    "Must have only 1 line per product for mass addition, but "
                    "there are %s lines for the product %s"
                    % (nr_lines, product.display_name),
                )
            )
        return result

    def _get_quick_line_qty_vals(self, product):
        return {
            "product_uom_qty": product.qty_to_process,
            "product_uom": product.quick_uom_id.id,
        }

    def _complete_quick_line_vals(self, vals, lines_key=""):
        # This params are need for playing correctly the onchange
        vals.update(
            {
                "order_id": self.id,
                "order_partner_id": self.partner_id.id,
            }
        )
        return super()._complete_quick_line_vals(vals, lines_key="order_line")

    def _add_quick_line(self, product, lines_key=""):
        return super()._add_quick_line(product, lines_key="order_line")
