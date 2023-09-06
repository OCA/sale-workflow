# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _is_commitment_date_a_public_holiday(self):
        """
        Returns True if commitment_date is a public holiday
        :return: bool
        """
        self.ensure_one()
        res = False
        if not self.commitment_date:
            return res
        commitment_date = fields.Datetime.context_timestamp(
            self, self.commitment_date
        ).date()
        partner = self.partner_shipping_id or self.partner_id
        domain = [
            ("year_id.country_id", "in", (False, partner.country_id.id)),
            "|",
            ("state_ids", "=", False),
            ("state_ids", "=", partner.state_id.id),
            ("date", "=", commitment_date),
        ]
        hhplo = self.env["hr.holidays.public.line"]
        holidays_line = hhplo.search(domain, limit=1, order="id")
        return bool(holidays_line)

    def check_commitment_date(self):
        """
        Returns True if the check is ok
        :return: bool
        """
        return not self._is_commitment_date_a_public_holiday()

    def _fields_trigger_check_exception(self):
        res = super()._fields_trigger_check_exception()
        res.append("commitment_date")
        return res
