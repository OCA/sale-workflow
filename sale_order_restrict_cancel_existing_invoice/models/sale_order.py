# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    confirmed_invoice_ids = fields.Many2many(
        comodel_name="account.invoice",
        compute="_compute_confirmed_invoice_ids",
        help="Technical field in order to retrieve confirmed invoices"
    )

    def _get_confirmed_invoice_states(self):
        """
        Return the invoice states that should avoid order cancel
        :return:
        """
        return ["open"]

    @api.multi
    @api.depends("invoice_ids")
    def _compute_confirmed_invoice_ids(self):
        for sale in self:
            sale.confirmed_invoice_ids = sale.invoice_ids.filtered(
                lambda i, states=self._get_confirmed_invoice_states():
                i.state in states)

    def action_cancel(self):
        if any(sale.confirmed_invoice_ids for sale in self):
            raise UserError(
                _("You cannot cancel a Sale Order for which a confirmed "
                  "invoice exists!"))
        return super(SaleOrder, self).action_cancel()
