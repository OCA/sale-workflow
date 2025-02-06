from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    partner_address_restriction_domain = fields.Binary(
        compute="_compute_partner_address_restriction_domain",
        help="This is the computed domain to filter delivery and invoicing addresses.",
    )

    @api.depends("partner_id", "company_id.sale_partner_address_restriction")
    def _compute_partner_address_restriction_domain(self):
        for activated, activated_sales in self.partition(
            lambda sale: sale.company_id.sale_partner_address_restriction
        ).items():
            if not activated:
                activated_sales.partner_address_restriction_domain = [(1, "=", 1)]
                continue
            for company, sales in activated_sales.partition("company_id").items():
                for sale in sales:
                    sale.partner_address_restriction_domain = [
                        ("commercial_partner_id", "=", sale.partner_id.id),
                        "|",
                        ("company_id", "=", False),
                        ("company_id", "=", company.id),
                    ]

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
