# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):

    _inherit = "sale.order"

    unpaid_invoice_ids = fields.Many2many(
        comodel_name="account.move",
        compute="_compute_confirmed_invoice_ids",
        help="Technical field in order to retrieve confirmed invoices",
    )

    def _get_paid_invoice_states(self):
        """
        Return the invoice move_type that should avoid order cancel
        :return:
        """
        return ["paid", "reversed"]

    @api.depends("invoice_ids")
    def _compute_confirmed_invoice_ids(self):
        for sale in self:
            sale.unpaid_invoice_ids = sale.invoice_ids.filtered(
                lambda i, payment_states=self._get_paid_invoice_states(): i.payment_state
                not in payment_states
            )

    def action_cancel(self):
        if any(sale.unpaid_invoice_ids for sale in self):
            raise UserError(
                _(
                    "You cannot cancel a Sale Order for which a confirmed "
                    "invoice exists!"
                )
            )
        return super(SaleOrder, self).action_cancel()
