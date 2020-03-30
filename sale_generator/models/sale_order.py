#  @author Sébastien BEAU <sebastien.beau@akretion.com>
#  @author EBII MonsieurB <monsieurb@saaslys.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    generator_id = fields.Many2one(
        comodel_name="sale.generator", string="Generator"
    )
    is_template = fields.Boolean(string="Is a generator template")
    active = fields.Boolean("Active", default=True)

    @api.model
    def create(self, vals):
        if self.env.context.get("tmpl_mode"):
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "sale.order.tmpl"
                )
            if not vals.get("partner_id"):
                vals["partner_id"] = self.env.ref(
                    "sale_generator.dummy_so_generator_partner"
                ).id
        return super().create(vals)
