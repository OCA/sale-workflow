from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    lot_id = fields.Many2one(
        comodel_name="stock.production.lot",
        string="Lot",
        domain="[('id', 'in', allowed_lot_ids)]",
        copy=False,
    )
    allowed_lot_ids = fields.Many2many(
        comodel_name="stock.production.lot",
        compute="_compute_allowed_lot_ids",
    )

    @api.depends("product_id")
    def _compute_allowed_lot_ids(self):
        lot_model = self.env["stock.production.lot"]
        for rec in self:
            rec.allowed_lot_ids = lot_model.search(
                [
                    ("product_id", "=", rec.product_id.id),
                ]
            )

    def _prepare_procurement_values(self, group_id=False):
        vals = super()._prepare_procurement_values(group_id=group_id)
        if self.lot_id:
            vals["restrict_lot_id"] = self.lot_id.id
        return vals

    @api.onchange("product_id")
    def product_id_change(self):
        res = super().product_id_change()
        self.lot_id = False
        return res
