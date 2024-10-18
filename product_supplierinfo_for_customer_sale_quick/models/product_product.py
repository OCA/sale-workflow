from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    product_customer_code = fields.Char(
        string="Product Customer Code",
        compute="_compute_product_customer_info",
        search="_search_customer_supplierinfo_data",
        readonly=True,
    )

    product_customer_name = fields.Char(
        string="Product Customer Name",
        compute="_compute_product_customer_info",
        search="_search_customer_supplierinfo_data",
        readonly=True,
    )

    @api.model
    def _search_customer_supplierinfo_data(self, operator, value):
        partner_id = self.env.context.get("partner_id")

        products = self.env["product.customerinfo"].search(
            [
                ("name", "=", partner_id),
                "|",
                ("product_name", operator, value),
                ("product_code", operator, value),
            ]
        )
        prod_filtered = products.filtered("product_id")

        res = prod_filtered.mapped("product_id") | (products - prod_filtered).mapped(
            "product_tmpl_id.product_variant_ids"
        )
        return [("id", "in", res.ids)]

    def _compute_product_customer_info(self):
        partner_id = self.env.context.get("partner_id")
        partner = self.env["res.partner"].browse(partner_id)
        for product in self:
            if partner.exists():
                supplier_info = product._select_customerinfo(partner=partner)
                product.product_customer_code = supplier_info.product_code
                product.product_customer_name = supplier_info.product_name
            else:
                product.product_customer_code = ""
                product.product_customer_name = ""
