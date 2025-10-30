# Copyright 2025 Akretion (https://www.akretion.com).
# @author Mathieu DELVA <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models

class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    packaging_id = fields.Many2one("product.packaging")

    def _is_applicable_for(self, product, qty_in_product_uom):
        ctx = self.env.context
        print("### _is_applicable_for TRIGGERED", ctx)
        if "packaging" in ctx:
            if ctx["packaging"] == self.packaging_id:
                return super()._is_applicable_for(product, qty_in_product_uom)
            return False

        elif "packaging" not in ctx and self.packaging_id:
            return False

        return super()._is_applicable_for(product, qty_in_product_uom)

    @classmethod
    def _get_applicable_rules(self, pricer_dict):
        """
        Surcharge de _get_applicable_rules pour garantir que les règles avec un packaging_id
        soient incluses dans le recordset initial si un packaging est passé dans le contexte.
        """
        applicable_rules = super()._get_applicable_rules(pricer_dict)
        print("### _get_applicable_rules TRIGGERED", self.env.context)
        packaging = self.env.context.get('packaging')
        
        if packaging:
            domain = [
                ('pricelist_id', 'in', applicable_rules.mapped('pricelist_id').ids),
                ('product_id', '=', pricer_dict['product'].id),
                ('packaging_id', '=', packaging.id),
            ]
            
            
            packaging_rules = self.search(domain)
            
            applicable_rules |= packaging_rules
            
        return applicable_rules.sorted(lambda r: (r.sequence, r.id))
    