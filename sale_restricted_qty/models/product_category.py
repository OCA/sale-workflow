# Copyright 2019 Akretion
# Copyright 2024 CorporateHub
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductCategory(models.Model):
    _name = "product.category"
    _inherit = ["product.category", "product.restricted.qty.mixin"]

    @api.depends("parent_id.is_sale_min_qty_set")
    def _compute_is_sale_inherited_min_qty_set(self):
        return super()._compute_is_sale_inherited_min_qty_set()

    def _get_is_sale_inherited_min_qty_set(self):
        if not self.parent_id:
            return super()._get_is_sale_inherited_min_qty_set()

        self.ensure_one()
        return self.parent_id.is_sale_min_qty_set

    @api.depends("parent_id.sale_min_qty")
    def _compute_sale_inherited_min_qty(self):
        return super()._compute_sale_inherited_min_qty()

    def _get_sale_inherited_min_qty(self):
        if not self.parent_id:
            return super()._get_sale_inherited_min_qty()

        self.ensure_one()
        return self.parent_id.sale_min_qty

    @api.depends("parent_id.is_sale_restrict_min_qty_set")
    def _compute_is_sale_inherited_restrict_min_qty_set(self):
        return super()._compute_is_sale_inherited_restrict_min_qty_set()

    def _get_is_sale_inherited_restrict_min_qty_set(self):
        if not self.parent_id:
            return super()._get_is_sale_inherited_restrict_min_qty_set()

        self.ensure_one()
        return self.parent_id.is_sale_restrict_min_qty_set

    @api.depends("parent_id.sale_restrict_min_qty")
    def _compute_sale_inherited_restrict_min_qty(self):
        return super()._compute_sale_inherited_restrict_min_qty()

    def _get_sale_inherited_restrict_min_qty(self):
        if not self.parent_id:
            return super()._get_sale_inherited_restrict_min_qty()

        self.ensure_one()
        return self.parent_id.sale_restrict_min_qty

    @api.depends("parent_id.is_sale_max_qty_set")
    def _compute_is_sale_inherited_max_qty_set(self):
        return super()._compute_is_sale_inherited_max_qty_set()

    def _get_is_sale_inherited_max_qty_set(self):
        if not self.parent_id:
            return super()._get_is_sale_inherited_max_qty_set()

        self.ensure_one()
        return self.parent_id.is_sale_max_qty_set

    @api.depends("parent_id.sale_max_qty")
    def _compute_sale_inherited_max_qty(self):
        return super()._compute_sale_inherited_max_qty()

    def _get_sale_inherited_max_qty(self):
        if not self.parent_id:
            return super()._get_sale_inherited_max_qty()

        self.ensure_one()
        return self.parent_id.sale_max_qty

    @api.depends("parent_id.is_sale_restrict_max_qty_set")
    def _compute_is_sale_inherited_restrict_max_qty_set(self):
        return super()._compute_is_sale_inherited_restrict_max_qty_set()

    def _get_is_sale_inherited_restrict_max_qty_set(self):
        if not self.parent_id:
            return super()._get_is_sale_inherited_restrict_max_qty_set()

        self.ensure_one()
        return self.parent_id.is_sale_restrict_max_qty_set

    @api.depends("parent_id.sale_restrict_max_qty")
    def _compute_sale_inherited_restrict_max_qty(self):
        return super()._compute_sale_inherited_restrict_max_qty()

    def _get_sale_inherited_restrict_max_qty(self):
        if not self.parent_id:
            return super()._get_sale_inherited_restrict_max_qty()

        self.ensure_one()
        return self.parent_id.sale_restrict_max_qty

    @api.depends("parent_id.is_sale_multiple_of_qty_set")
    def _compute_is_sale_inherited_multiple_of_qty_set(self):
        return super()._compute_is_sale_inherited_multiple_of_qty_set()

    def _get_is_sale_inherited_multiple_of_qty_set(self):
        if not self.parent_id:
            return super()._get_is_sale_inherited_multiple_of_qty_set()

        self.ensure_one()
        return self.parent_id.is_sale_multiple_of_qty_set

    @api.depends("parent_id.sale_multiple_of_qty")
    def _compute_sale_inherited_multiple_of_qty(self):
        return super()._compute_sale_inherited_multiple_of_qty()

    def _get_sale_inherited_multiple_of_qty(self):
        if not self.parent_id:
            return super()._get_sale_inherited_multiple_of_qty()

        self.ensure_one()
        return self.parent_id.sale_multiple_of_qty

    @api.depends("parent_id.is_sale_restrict_multiple_of_qty_set")
    def _compute_is_sale_inherited_restrict_multiple_of_qty_set(self):
        return super()._compute_is_sale_inherited_restrict_multiple_of_qty_set()

    def _get_is_sale_inherited_restrict_multiple_of_qty_set(self):
        if not self.parent_id:
            return super()._get_is_sale_inherited_restrict_multiple_of_qty_set()

        self.ensure_one()
        return self.parent_id.is_sale_restrict_multiple_of_qty_set

    @api.depends("parent_id.sale_restrict_multiple_of_qty")
    def _compute_sale_inherited_restrict_multiple_of_qty(self):
        return super()._compute_sale_inherited_restrict_multiple_of_qty()

    def _get_sale_inherited_restrict_multiple_of_qty(self):
        if not self.parent_id:
            return super()._get_sale_inherited_restrict_multiple_of_qty()

        self.ensure_one()
        return self.parent_id.sale_restrict_multiple_of_qty
