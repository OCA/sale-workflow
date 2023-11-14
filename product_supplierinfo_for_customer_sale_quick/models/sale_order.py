from odoo import _, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_context_add_products(self):
        res = super()._get_context_add_products()
        res.update(
            {
                "partner_id": self.partner_id.id,
            }
        )
        return res

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
        res["search_view_id"] = (
            self.env.ref(
                "product_supplierinfo_for_customer_sale_quick.product_search_form_view"
            ).id,
        )
        return res
