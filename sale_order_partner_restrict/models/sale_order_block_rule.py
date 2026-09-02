# Copyright 2026 Juan Carlos Oñate - Tecnativa <juancarlos.onate@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderBlockRule(models.Model):
    _name = "sale.order.block.rule"
    _description = "Sale Order Block Rule"
    _order = "id"

    name = fields.Char(required=True, help="Rule name for identification")
    active = fields.Boolean(default=True)
    partner_field = fields.Selection(
        selection=[
            ("email", "Email"),
            ("phone", "Phone"),
            ("mobile", "Mobile"),
            ("vat", "VAT"),
            ("zip", "ZIP Code"),
            ("street", "Street"),
            ("city", "City"),
            ("country_id", "Country"),
            ("state_id", "State"),
        ],
        required=True,
        help="Partner field to validate",
    )
    partner_scope = fields.Selection(
        selection=[
            ("all", "All addresses"),
            ("invoice", "Customer / Invoice address"),
            ("delivery", "Delivery address"),
        ],
        default="all",
        required=True,
        help="Order address(es) this rule is evaluated against",
    )
    blocked_values = fields.Text(
        help="Blocked values (comma-separated list)",
    )
    country_id = fields.Many2one(
        comodel_name="res.country",
        string="Country Filter",
        help="Optional: Apply this rule only for this specific country. "
        "Useful for blocking ZIP codes by country (e.g., Spanish ZIPs 35001-35999)",
    )
    zip_range_from = fields.Char(
        string="ZIP From",
        help="Starting ZIP code for range blocking",
    )
    zip_range_to = fields.Char(
        string="ZIP To",
        help="Ending ZIP code for range blocking",
    )
    block_message = fields.Text(
        required=True,
        default="Partner blocked by security rule",
        help="Custom message to display in chatter when order is canceled",
    )

    @api.onchange("partner_field")
    def _onchange_partner_field(self):
        if self.partner_field != "zip":
            self.country_id = False
            self.zip_range_from = False
            self.zip_range_to = False

    def _check_value_in_range(self, value_str, range_from, range_to):
        if not range_from or not range_to:
            return False
        try:
            value_num = int(value_str)
            from_num = int(range_from)
            to_num = int(range_to)
            return from_num <= value_num <= to_num
        except ValueError:
            return False

    def _check_partner_blocked(self, partner):
        self.ensure_one()
        if self.country_id and partner.country_id != self.country_id:
            return False, "", "", ""
        field_value = partner[self.partner_field]
        if self.partner_field in ("country_id", "state_id"):
            field_value = field_value.name if field_value else ""
        field_value_str = str(field_value or "").strip()
        if not field_value_str:
            return False, "", "", ""
        is_blocked = False
        if self.partner_field == "zip" and self.zip_range_from and self.zip_range_to:
            is_blocked = self._check_value_in_range(
                field_value_str, self.zip_range_from, self.zip_range_to
            )
        if not is_blocked and self.blocked_values:
            blocked_list = [
                v.strip() for v in self.blocked_values.split(",") if v.strip()
            ]
            is_blocked = field_value_str.lower() in [v.lower() for v in blocked_list]
        if is_blocked:
            field_label = dict(self._fields["partner_field"].selection).get(
                self.partner_field, self.partner_field
            )
            return True, self.block_message, field_label, field_value_str
        return False, "", "", ""
