from odoo import _, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval


class SaleBlanketOrder(models.Model):
    _name = "sale.blanket.order"
    _inherit = ["sale.blanket.order", "product.mass.addition"]

    def _get_context_add_products(self):
        res = {
            "search_default_filter_to_sale": 1,
            "quick_access_rights_sale": 1,
        }
        return res

    def _get_domain_add_products(self):
        field = self.env["sale.blanket.order.line"]._fields.get("product_id")
        field_domain = field.domain
        if not isinstance(field_domain, str):
            field_domain = str(field_domain)
        return safe_eval(field_domain, {"company_id": self.company_id.id})

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
        result = self.line_ids.filtered(lambda rec: rec.product_id == product)

        nr_lines = len(result.ids)
        if nr_lines > 1:
            raise ValidationError(
                _(
                    "Must have only 1 line per product for mass addition, but "
                    "there are %(lines)s lines for the product %(product)s",
                    lines=nr_lines,
                    product=product.display_name,
                )
            )
        return result

    def _get_quick_line_qty_vals(self, product):
        return {
            "original_uom_qty": product.qty_to_process,
            "product_uom": product.quick_uom_id.id,
            "price_unit": product.list_price,
        }

    def _complete_quick_line_vals(self, vals, lines_key=""):
        vals.update(
            {
                "order_id": self.id,
            }
        )
        return super()._complete_quick_line_vals(vals, lines_key="line_ids")

    def _add_quick_line(self, product, lines_key=""):
        return super()._add_quick_line(product, lines_key="line_ids")
