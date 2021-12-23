from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_order_partner_restrict = fields.Selection(
        related="company_id.sale_order_partner_restrict",
        string="Partner Restriction on Sale Orders",
    )

    def _get_partner_restrict_domain(self):
        partner_restrict_domain = []
        if (
            self.sale_order_partner_restrict == "all"
            or self.sale_order_partner_restrict is None
        ):
            partner_restrict_domain = [
                "|",
                ("company_id", "=", False),
                ("company_id", "=", self.company_id.id),
            ]
        elif self.sale_order_partner_restrict == "only_parents":
            partner_restrict_domain = [
                "&",
                ("parent_id", "=", False),
                "|",
                ("company_id", "=", False),
                ("company_id", "=", self.company_id.id),
            ]
        elif self.sale_order_partner_restrict == "parents_and_contacts":
            partner_restrict_domain = [
                "&",
                "|",
                ("company_id", "=", False),
                ("company_id", "=", self.company_id.id),
                "|",
                ("parent_id", "=", False),
                ("type", "=", "contact"),
            ]
        return partner_restrict_domain

    @api.onchange("sale_order_partner_restrict")
    def _onchange_sale_order_partner_restrict(self):
        self.ensure_one()
        return {"domain": {"partner_id": self._get_partner_restrict_domain()}}

    @api.constrains("partner_id")
    def _check_order_partner_restrict(self):
        for order in self:
            domain = order._get_partner_restrict_domain()
            if not order.partner_id.search(
                expression.AND([[("id", "=", order.partner_id.id)], domain])
            ):
                raise ValidationError(
                    _("The Customer %s is not available for this company (%s).")
                    % (order.partner_id.name, order.company_id.name)
                )
