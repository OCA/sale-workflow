# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2025 Openforce Srls Unipersonale (www.openforce.it)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.constrains("name")
    def _check_unique_name_in_company(self):
        orders = self.filtered(lambda so: so.name and so.company_id)
        if not orders:
            return

        grouped_orders = self.env["sale.order"].read_group(
            domain=[
                ("name", "in", orders.mapped("name")),
                ("company_id", "in", orders.mapped("company_id").ids),
            ],
            fields=["name", "company_id"],
            groupby=["name", "company_id"],
            lazy=False,
        )
        duplicate_keys = {
            (group["name"], group["company_id"][0])
            for group in grouped_orders
            if group.get("__count", 0) > 1
        }
        for so in orders:
            if (so.name, so.company_id.id) in duplicate_keys:
                raise ValidationError(
                    _("Sale Order name must be unique within a company!")
                )
