# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def create_invoices(self):
        skip = self._skip_invoice_mail()
        wiz = self.with_context(mail_auto_subscribe_no_notify=skip)
        return super(SaleAdvancePaymentInv, wiz).create_invoices()

    def _skip_invoice_mail(self):
        """Hook method, can be overridden. Returns True by default"""
        return True
