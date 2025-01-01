# Copyright 2022 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleAttachedProductMixin(models.AbstractModel):
    _name = "sale.attached.product.mixin"
    _description = "Mixin class for sale attached product features"

    @api.model
    def _get_auto_refresh_attached_product_triggers(self) -> set:
        """Returns set of fields which trigger the recomputation.
        The method is overriden in the proper modules to set the proper triggers though
        """
        return set()

    def _get_recs_data(self) -> list:
        """Allows to optimize the comparison before and after the write for the
        minimum possible set of fields"""
        triggers = self._get_auto_refresh_attached_product_triggers()
        recs_data = []
        for rec in self:
            data = {}
            for dotted_field_name in triggers:
                val = rec.mapped(dotted_field_name)
                if isinstance(val, models.AbstractModel):
                    val = val.ids
                data[dotted_field_name] = val
            recs_data.append({rec: data})
        return recs_data

    def _check_skip_attached_product_refresh(self):
        """Checks whether refresh should be skipped

        Hook method to be overridden if necessary
        :return: True if auto-refresh should be skipped
        """
        ctx = self.env.context
        return ctx.get("skip_auto_refresh_attached_product")
