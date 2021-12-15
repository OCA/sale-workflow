from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_order_partner_restrict = fields.Selection(
        related="company_id.sale_order_partner_restrict",
        string="Partner Restriction on Sale Orders",
    )
    available_partners = fields.Many2many(
        "res.partner", compute="_compute_available_partners"
    )

    @api.onchange("available_partners")
    def _on_change_available_partner_ids(self):
        self.ensure_one()
        return {"domain": {"partner_id": [("id", "in", self.available_partners.ids)]}}

    @api.depends("partner_id", "sale_order_partner_restrict")
    def _compute_available_partners(self):
        for order in self:
            if (
                order.sale_order_partner_restrict == "all"
                or order.sale_order_partner_restrict is None
            ):
                order.available_partners = self.env["res.partner"].search(
                    [
                        "|",
                        ("company_id", "=", False),
                        ("company_id", "=", order.company_id.id),
                    ]
                )
            elif order.sale_order_partner_restrict == "only_parents":
                order.available_partners = self.env["res.partner"].search(
                    [
                        "&",
                        ("parent_id", "=", False),
                        "|",
                        ("company_id", "=", False),
                        ("company_id", "=", order.company_id.id),
                    ]
                )
            elif order.sale_order_partner_restrict == "parents_and_contacts":
                order.available_partners = self.env["res.partner"].search(
                    [
                        "&",
                        "|",
                        ("company_id", "=", False),
                        ("company_id", "=", order.company_id.id),
                        "|",
                        ("parent_id", "=", False),
                        ("type", "=", "contact"),
                    ]
                )

    @api.constrains("partner_id")
    def _check_order_partner_restrict(self):
        for order in self:
            if order.partner_id not in order.available_partners:
                raise ValidationError(
                    _("The Customer %s is not available for this company (%s).")
                    % (order.partner_id.name, order.company_id.name)
                )
