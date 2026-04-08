# Copyright 2026 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    is_pto = fields.Boolean(
        compute="_compute_is_pto",
        inverse="_inverse_is_pto",
        store=True,
        recursive=True,
        readonly=False,
        help=(
            "Technical field indicating whether this location"
            " belongs to a put-to-order area."
        ),
    )
    parent_is_pto = fields.Boolean(
        compute="_compute_parent_is_pto",
        help=(
            "Technical field indicating whether the parent"
            " location is a put-to-order area."
        ),
    )

    @api.depends("location_id.is_pto")
    def _compute_is_pto(self):
        for location in self:
            if location.location_id:
                location.is_pto = location.location_id.is_pto

    def _inverse_is_pto(self):
        return

    @api.depends("location_id.is_pto")
    def _compute_parent_is_pto(self):
        for location in self:
            location.parent_is_pto = bool(location.location_id.is_pto)

    def _search_pto(
        self, excluded_locations=None, company=None, extra_domain=None, limit=None
    ):
        """Search child locations of this PTO root."""
        if not self:
            return self.browse()
        domain = [("id", "child_of", self.id)]
        if excluded_locations:
            domain.append(("id", "not in", excluded_locations.ids))
        if company:
            domain.append(("company_id", "=", company.id))
        if extra_domain:
            domain += extra_domain
        return self.search(domain, limit=limit)
