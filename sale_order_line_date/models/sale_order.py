# © 2016 OdooMRP team
# © 2016 AvanzOSC
# © 2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2016 ForgeFlow S.L. (https://forgeflow.com)
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange("expected_date", "commitment_date")
    def _onchange_commitment_date(self):
        """Update order lines with commitment date from sale order"""
        result = super(SaleOrder, self)._onchange_commitment_date() or {}
        if "warning" not in result:
            for line in self.order_line:
                if not line.commitment_date or (
                    self.expected_date and line.commitment_date < self.expected_date
                ):
                    line.commitment_date = self.commitment_date
        return result
