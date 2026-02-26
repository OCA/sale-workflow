# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.http import route

from odoo.addons.website_sale.controllers.variant import WebsiteSaleVariantController


class WebsiteSaleRoundingVariantController(WebsiteSaleVariantController):
    @route(
        "/website_sale/get_combination_info",
        type="jsonrpc",
        auth="public",
        methods=["POST"],
        website=True,
        readonly=True,
    )
    def get_combination_info_website(
        self,
        product_template_id,
        product_id,
        combination,
        add_qty,
        uom_id=None,
        **kwargs,
    ):
        combination_info = super().get_combination_info_website(
            product_template_id=product_template_id,
            product_id=product_id,
            combination=combination,
            add_qty=add_qty,
            uom_id=uom_id,
            **kwargs,
        )
        incoming_pid = int(product_id or 0)
        resolved_pid = int(combination_info.get("product_id") or 0)

        # Detect if the variant has changed to be able
        # to reset the quantity to the default value for the new variant if needed.
        combination_info["variant_switched"] = bool(
            resolved_pid and resolved_pid != incoming_pid
        )
        return combination_info
