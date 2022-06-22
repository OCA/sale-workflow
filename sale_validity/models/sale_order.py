# © 2013-2017 Camptocamp SA
# © 2014-2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    validity_date = fields.Date(
        tracking=True, default=lambda rec: rec._default_validity_date()
    )

    @api.model
    def _default_validity_date(self):
        validity_date_str = False
        company = self.env.company
        if company.default_sale_order_validity_days:
            today_str = fields.Date.context_today(self)
            today = fields.Date.to_date(today_str)
            validity_date = today + relativedelta(
                days=company.default_sale_order_validity_days
            )
            validity_date_str = fields.Date.to_string(validity_date)
        return validity_date_str

    @api.onchange("date_order")
    def _onchange_date_order(self):
        if self.date_order:
            company = self.company_id or self.env.company
            if company.default_sale_order_validity_days:
                date_order = fields.Datetime.to_datetime(self.date_order)
                validity_date = date_order + relativedelta(
                    days=company.default_sale_order_validity_days
                )
                self.validity_date = fields.Date.to_string(validity_date)
