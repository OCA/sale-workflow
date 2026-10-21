# Copyright 2026 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    @api.model
    def _bom_find(self, products, picking_type=None, company_id=False, bom_type=False):
        bom_by_product = super()._bom_find(
            products,
            picking_type=picking_type,
            company_id=company_id,
            bom_type=bom_type,
        )
        kit_id = self.env.context.get("sale_mrp_bom_kit_id")
        if not kit_id or bom_type not in (False, "phantom"):
            return bom_by_product
        kit = self.browse(kit_id)
        for product in products:
            if kit.product_id == product or (
                not kit.product_id and kit.product_tmpl_id == product.product_tmpl_id
            ):
                bom_by_product[product] = kit
        return bom_by_product
