# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)
from datetime import timedelta

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _prepare_procurement_values(self, group_id=False):
        """ Prepare specific key for moves or other components that will be created from
        a stock rule comming from a sale order line. This method could be override in order
        to add other custom key that could be used in move/po creation.
        """
        values = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        self.ensure_one()
        date_planned = self.order_id.confirmation_date \
            + timedelta(days=self.customer_lead or 0.0) - timedelta(
                days=self.order_id.company_id.security_lead)
        values.update({
            'company_id': self.order_id.company_id,
            'group_id': group_id,
            'sale_line_id': self.id,
            'date_planned': date_planned,
            'route_ids': self.route_id,
            'warehouse_id': self.order_id.warehouse_id or False,
            'partner_id': self.order_id.partner_shipping_id.id,
        })
        default_route = self.order_id.partner_id.default_route
        if default_route and not self.route_id:
            values.update({
                'route_ids': default_route,
            })
        for line in self.filtered("order_id.commitment_date"):
            date_planned = fields.Datetime.from_string(line.order_id.commitment_date)\
                - timedelta(days=line.order_id.company_id.security_lead)
            values.update({
                'date_planned': fields.Datetime.to_string(date_planned),
            })
        return values
