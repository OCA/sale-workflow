from odoo import _, api, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.constrains("partner_id", "partner_invoice_id", "partner_shipping_id")
    def _check_partner_addresses(self):
        for order in self:
            if (
                order.company_id.sale_partner_address_restriction
                and order.partner_id
                and (
                    (order.partner_invoice_id.commercial_partner_id != order.partner_id)
                    or (
                        order.partner_shipping_id.commercial_partner_id
                        != order.partner_id
                    )
                )
            ):
                raise ValidationError(
                    _(
                        "Invoice and shipping addresses must be child addresses"
                        " of the selected partner or the selected partner itself."
                    )
                )
