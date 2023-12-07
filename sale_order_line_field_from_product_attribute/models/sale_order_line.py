# Copyright (C) 2023 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def write(self, vals):
        res = super().write(vals)
        if "product_no_variant_attribute_value_ids" in vals:
            for sol in self:
                sol_pav = sol.product_no_variant_attribute_value_ids
                sol_pav_to_store = sol_pav.filtered("attribute_id.store_in_field")
                sol_pav_custom = sol.product_custom_attribute_value_ids
                pav_vals = {}
                for pav in sol_pav_to_store:
                    field_name = pav.attribute_id.store_in_field.name
                    value = (
                        sol_pav_custom.filtered(
                            lambda x: x.custom_product_template_attribute_value_id
                            == pav
                        ).custom_value
                        or pav.name
                    )
                    pav_vals[field_name] = value
                if pav_vals:
                    super().write(pav_vals)
        return res
