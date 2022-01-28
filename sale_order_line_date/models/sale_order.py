# © 2016 OdooMRP team
# © 2016 AvanzOSC
# © 2016 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2016 ForgeFlow S.L. (https://forgeflow.com)
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange("expected_date")
    def _onchange_expected_date(self):
        """
        Every time a sale order line Delivery Date is changed,
        this method is called.
        """
        res = super(SaleOrder, self)._onchange_expected_date()
        dates_list = []
        for line in self.order_line.filtered(
            lambda x: x.state != "cancel"
            and not x._is_delivery()
            and not x.display_type
        ):
            if line.commitment_date:
                dt = line.commitment_date
                dates_list.append(dt)
        if dates_list:
            commitment_date = (
                min(dates_list) if self.picking_policy == "direct" else max(dates_list)
            )
            self.commitment_date = fields.Datetime.to_string(commitment_date)
        else:
            return res

    @api.onchange("commitment_date")
    def _onchange_commitment_date(self):
        self._onchange_expected_date()
