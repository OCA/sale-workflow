from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def get_product_multiline_description_sale(self):
        self = self.with_context(include_single_value=True)
        return super(ProductProduct, self).get_product_multiline_description_sale()


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"

    def _get_combination_name(self):
        if self.env.context.get("include_single_value"):
            ptavs = self._without_no_variant_attributes().with_prefetch(
                self._prefetch_ids
            )
            return ", ".join([ptav.name for ptav in ptavs])
        else:
            return super(ProductTemplateAttributeValue, self)._get_combination_name()
