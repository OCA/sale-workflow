# © 2010-2012 Andy Lu <andy.lu@elico-corp.com> (Elico Corp)
# © 2013 Agile Business Group sagl (<http://www.agilebg.com>)
# © 2017 valentin vinagre  <valentin.vinagre@qubiq.es> (QubiQ)
# © 2020 Manuel Regidor  <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if self.is_using_quotation_number(vals):
                sequence = self.env["ir.sequence"].next_by_code("sale.quotation")
                vals["name"] = sequence or "/"
        return super().create(vals_list)

    @api.model
    def is_using_quotation_number(self, vals):
        company = False
        if "company_id" in vals:
            company = self.env["res.company"].browse(vals.get("company_id"))
        else:
            company = self.env.company
        return not company.keep_name_so

    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        if self.origin and self.origin != "":
            default["origin"] = self.origin + ", " + self.name
        else:
            default["origin"] = self.name
        return super().copy(default)

    def action_confirm(self):
        for order in self:
            if self.name[:2] != "SQ":
                continue
            if order.state not in ("draft", "sent") or order.company_id.keep_name_so:
                continue
            if order.origin and order.origin != "":
                quo = order.origin + ", " + order.name
            else:
                quo = order.name
            sequence = self.env["ir.sequence"].next_by_code("sale.order")
            order.write({"origin": quo, "name": sequence})
        return super().action_confirm()
