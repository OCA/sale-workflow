# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_customerinfo_display_name(self):
        """Product name with the customer code and name, as in 19.0."""
        self.ensure_one()
        if not (
            self.product_id
            and self.move_id.is_sale_document(include_receipts=True)
            and self.sale_line_ids.filtered("product_customer_code")
        ):
            return False
        product = self.product_id.with_context(lang=self.move_id._get_lang())
        customerinfo = product._select_customerinfo(partner=self.move_id.partner_id)
        if not customerinfo.product_code:
            return False
        name = (
            customerinfo.product_name
            or product.with_context(display_default_code=False).display_name
        )
        return f"[{customerinfo.product_code}] {name}"

    @api.depends("sale_line_ids", "move_id.partner_id")
    def _compute_label(self):
        res = super()._compute_label()
        for line in self:
            display_name = line._get_customerinfo_display_name()
            if not display_name:
                continue
            if not line.name:
                line.label = display_name
            elif line.name.splitlines()[0] == display_name:
                line.label = line.name
            else:
                line.label = display_name + "\n" + line.name
        return res

    def _inverse_label(self):
        res = super()._inverse_label()
        for line in self:
            display_name = line._get_customerinfo_display_name()
            if display_name and line.label:
                line.name = line.label.removeprefix(display_name).removeprefix("\n")
        return res
