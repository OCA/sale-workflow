# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, models
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _check_sale_orders_fully_invoiced(
        self,
    ):
        for sale_order in self.sale_order_ids:
            if sale_order.invoice_status == "invoiced" and sale_order.force_invoiced:
                raise UserError(
                    _(
                        "The order %(name)s is forced as invoiced. "
                        "You should first remove this flag to create a new invoice.",
                        name=sale_order.name,
                    )
                )

    def create_invoices(self):
        self._check_sale_orders_fully_invoiced()
        return super().create_invoices()
