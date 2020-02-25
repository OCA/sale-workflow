#  @author Sébastien BEAU <sebastien.beau@akretion.com>
#  @author EBII MonsieurB <monsieurb@saaslys.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
from lxml import etree


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
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "sale.order.tmpl"
            ) or _("New template")
            if not vals.get("partner_id"):
                # in tmpl_mode we hide partner_id and don't care about its value
                vals["partner_id"] = (
                    self.env["res.partner"].search([], limit=1).id
                )
        return super().create(vals)

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        res = super(SaleOrder, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu,
        )
        doc = etree.XML(res["arch"])
        if view_type == "form":
            for node in doc.xpath("//button"):
                node.getparent().remove(node)
            for node in doc.xpath("//field[@name='sale_order_template_id']"):
                node.getparent().remove(node)
            for node in doc.xpath("//field[@name='state']"):
                node.set("statusbar_visible", "quotation")
        res["arch"] = etree.tostring(doc, encoding="unicode")
        return res
