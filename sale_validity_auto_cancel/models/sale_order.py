# Copyright 2023 ForgeFlow S.L.
# Copyright 2024 OERP Canada <https://www.oerp.ca>
# Copyright 2026 ACSONE SA/NV (<https://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import logging

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    auto_cancel_expired_so = fields.Boolean(
        related="partner_id.auto_cancel_expired_so", string="Auto Cancel"
    )

    @api.model
    def _get_auto_cancel_expired_states(self):
        """Returns the states of an order that can be auto canceled"""
        return ["draft", "sent"]

    @api.model
    def _prepare_auto_cancel_expired_domain(self, company):
        """Returns a domain allowing expired order retrieval

        :param company: a company record to filter from
        """
        threshold = fields.Date.today() - relativedelta(
            days=company.sale_validity_auto_cancel_days
        )
        return [
            ("company_id", "=", company.id),
            ("state", "in", self._get_auto_cancel_expired_states()),
            ("validity_date", "<", threshold),
            ("auto_cancel_expired_so", "=", True),
        ]

    @api.model
    def cron_sale_validity_auto_cancel(self, company_ids=None):
        """Auto cancel expired sale orders for companies in company_ids.
        If company_ids is None, all companies are considered.

        :param company_ids: list of company ids to consider
        """
        company_domain = []
        if company_ids:
            company_domain.append(("id", "in", company_ids))
        companies = self.env["res.company"].search(company_domain)
        for company in companies:
            orders = self.env["sale.order"].search(
                self._prepare_auto_cancel_expired_domain(company)
            )
            for order in orders:
                try:
                    order.with_context(company_id=company.id)._action_cancel()
                except Exception as e:
                    _logger.error("Failed to auto-cancel %s: %s", order.name, str(e))
