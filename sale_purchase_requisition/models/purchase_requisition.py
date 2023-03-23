# Copyright 2023 Moduon Team S.L. <info@moduon.team>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    sale_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale Order",
        help="Sale order related to this purchase requisition.",
    )
    sale_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Sale Representative",
        related="sale_id.user_id",
    )
    purchase_requisition_sync_warning = fields.Char(compute="_compute_sync_sale_order")

    def _compute_sync_sale_order(self):
        for rec in self:
            rec.purchase_requisition_sync_warning = False
            if rec.sale_id._unsynced_prs():
                rec.purchase_requisition_sync_warning = _(
                    "Some lines are not synced on this Sale order: %s. "
                    "Please update these lines manually.",
                    rec.sale_id.name,
                )


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    line_order_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Sale Order Line",
    )

    def write(self, values):
        for rec in self:
            if "product_qty" in values and values["product_qty"] != rec.product_qty:
                rec.requisition_id.message_post(
                    body=_(
                        "The product quantities %(product)s <br/>"
                        "  have changed %(old_qty)d -> %(new_qty)d %(uom)s",
                        product=rec.product_id.name,
                        old_qty=rec.product_qty,
                        new_qty=values["product_qty"],
                        uom=rec.product_uom_id.name,
                    )
                )
        return super().write(values)
