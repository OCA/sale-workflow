# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_order_type(self):
        return self.env["sale.order.type"].search([], limit=1)

    type_id = fields.Many2one(
        comodel_name="sale.order.type", string="Type", default=_get_order_type
    )

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        super(SaleOrder, self).onchange_partner_id()
        sale_type = (
            self.partner_id.sale_type or self.partner_id.commercial_partner_id.sale_type
        )
        if sale_type:
            self.type_id = sale_type

    @api.onchange("type_id")
    def onchange_type_id(self):
        vals = {}
        for order in self:
            vals = {}
            order_type = order.type_id
            if order_type.warehouse_id:
                vals.update({"warehouse_id": order_type.warehouse_id})
            if order_type.picking_policy:
                vals.update({"picking_policy": order_type.picking_policy})
            if order_type.payment_term_id:
                vals.update({"payment_term_id": order_type.payment_term_id})
            if order_type.pricelist_id:
                vals.update({"pricelist_id": order_type.pricelist_id})
            if order_type.incoterm_id:
                vals.update({"incoterm": order_type.incoterm_id})
            if vals:
                order.update(vals)

    @api.model
    def create(self, vals):
        if vals.get("name", "/") == "/" and vals.get("type_id"):
            sale_type = self.env["sale.order.type"].browse(vals["type_id"])
            if sale_type.sequence_id:
                vals["name"] = sale_type.sequence_id.next_by_id()
        return super(SaleOrder, self).create(vals)

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        if self.type_id.journal_id:
            res["journal_id"] = self.type_id.journal_id.id
        if self.type_id:
            res["sale_type_id"] = self.type_id.id
        return res
