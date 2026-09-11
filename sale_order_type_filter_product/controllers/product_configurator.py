from odoo.http import request

from odoo.addons.sale.controllers.product_configurator import (
    SaleProductConfiguratorController,
)


class SaleOrderTypeProductConfiguratorController(SaleProductConfiguratorController):
    def _get_product_information(
        self,
        product_template,
        combination,
        currency,
        pricelist,
        so_date,
        quantity=1,
        product_uom_id=None,
        parent_combination=None,
        **kwargs,
    ):
        values = super()._get_product_information(
            product_template,
            combination,
            currency,
            pricelist,
            so_date,
            quantity=quantity,
            product_uom_id=product_uom_id,
            parent_combination=parent_combination,
            **kwargs,
        )
        sale_order_type_id = kwargs.get("sale_order_type_id")
        if sale_order_type_id:
            sale_order_type = request.env["sale.order.type"].browse(sale_order_type_id)
            invalid_variants = product_template.product_variant_ids.filtered(
                lambda product: (
                    product._get_allowed_sale_order_types()
                    and sale_order_type not in product._get_allowed_sale_order_types()
                )
            )
            archived_combinations = values["archived_combinations"]
            for product in invalid_variants:
                combination_ids = product.product_template_attribute_value_ids.ids
                if combination_ids not in archived_combinations:
                    archived_combinations.append(combination_ids)
        return values
