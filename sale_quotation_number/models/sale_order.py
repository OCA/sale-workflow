from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if self._is_using_quotation_number(vals):
                sequence = self.env["ir.sequence"].next_by_code("sale.quotation")
                vals["name"] = sequence or "/"
        return super(SaleOrder, self).create(vals_list)

    @api.model
    def _is_using_quotation_number(self, vals):
        if "company_id" in vals:
            company = self.env["res.company"].browse(vals.get("company_id"))
        else:
            company = self.env.company
        return not company.keep_name_so

    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        if self.origin:
            default["origin"] = self.origin + ", " + self.name
        else:
            default["origin"] = self.name
        return super(SaleOrder, self).copy(default)

    def action_confirm(self):
        for order in self.filtered(lambda so: not so.company_id.keep_name_so):
            if order.origin:
                quo = order.origin + ", " + order.name
            else:
                quo = order.name
            sequence = self.env["ir.sequence"].next_by_code("sale.order")
            order.write({"origin": quo, "name": sequence})
        return super(SaleOrder, self).action_confirm()
