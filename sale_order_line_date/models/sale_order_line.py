# © 2016 OdooMRP team
# © 2016 AvanzOSC
# © 2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2016 ForgeFlow S.L. (https://forgeflow.com)
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from datetime import timedelta

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    commitment_date = fields.Datetime("Delivery Date")

    def _prepare_procurement_values(self, group_id=False):
        vals = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        # has ensure_one already
        if self.commitment_date:
            vals.update(
                {
                    "date_planned": self.commitment_date
                    - timedelta(days=self.order_id.company_id.security_lead)
                }
            )
            vals.update({"date_deadline": self.commitment_date})
        return vals

    def _expected_date(self):
        """
        The only intention of this method is to call
        _onchange_expected_date() when a sale order line
        Delivery Date is changed and SO was already confirmed.
        """
        res = super(SaleOrderLine, self)._expected_date()
        self.order_id._onchange_expected_date()
        return res
