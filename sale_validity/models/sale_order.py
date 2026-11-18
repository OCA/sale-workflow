# © 2013-2017 Camptocamp SA
# © 2014-2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    validity_date = fields.Date(tracking=True)

    @api.depends("date_order", "company_id")
    def _compute_validity_date(self):
        super()._compute_validity_date()
        for order in self:
            company = order.company_id or order.env.company
            if company.default_sale_order_validity_days and order.date_order:
                date_order = fields.Datetime.to_datetime(order.date_order)
                order.validity_date = fields.Date.to_date(
                    date_order
                    + relativedelta(days=company.default_sale_order_validity_days)
                )
        return
