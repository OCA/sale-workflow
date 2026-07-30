# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("partner_id", "partner_shipping_id")
    def _compute_warehouse_id(self):
        draft_orders = self.filtered(lambda s: s.state == "draft")
        to_super = self - draft_orders
        for sale in draft_orders:
            warehouse = False
            if sale.company_id.sale_warehouse_by_partner_shipping:
                warehouse = sale.partner_shipping_id.with_company(
                    sale.company_id
                ).sale_warehouse_id
            warehouse = (
                warehouse
                or sale.partner_id.with_company(sale.company_id).sale_warehouse_id
            )
            if warehouse:
                sale.warehouse_id = warehouse
                continue
            to_super |= sale
        if to_super:
            return super(SaleOrder, to_super)._compute_warehouse_id()
