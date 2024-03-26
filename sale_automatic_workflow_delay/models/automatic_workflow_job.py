# © 2021 initOS GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re
from datetime import datetime, timedelta

from odoo import api, models


class AutomaticWorkflowJob(models.Model):
    _inherit = "automatic.workflow.job"

    @api.model
    def _get_delay(self, job):
        param = self.env["ir.config_parameter"].get_param(
            f"sale.automatic.workflow.{job}.delay", "15"
        )

        if re.match(r"^\d+$", param):
            time = datetime.now() - timedelta(minutes=int(param))
            return [("create_date", "<", time)]
        return []

    @api.model
    def _validate_sale_orders(self, domain_filter):
        domain_filter.extend(self._get_delay("sale.order.validate"))
        return super()._validate_sale_orders(domain_filter)

    @api.model
    def _sale_done(self, domain_filter):
        domain_filter.extend(self._get_delay("sale.order.done"))
        return super()._sale_done(domain_filter)

    @api.model
    def _validate_pickings(self, domain_filter):
        domain_filter.extend(self._get_delay("stock.picking.validate"))
        return super()._validate_pickings(domain_filter)

    @api.model
    def _validate_invoices(self, domain_filter):
        domain_filter.extend(self._get_delay("account.move.validate"))
        return super()._validate_invoices(domain_filter)

    @api.model
    def _create_invoices(self, domain_filter):
        domain_filter.extend(self._get_delay("account.move.create"))
        return super()._create_invoices(domain_filter)
