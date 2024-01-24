from odoo import api, fields, models


class SaleBlanketOrderLine(models.Model):
    _inherit = "sale.blanket.order.line"

    product_customer_reference = fields.Char(
        compute="_compute_product_customer_reference",
        string="Customer Reference",
        store=True,
    )

    @api.depends("product_id")
    def _compute_product_customer_reference(self):
        for line in self:
            customer_reference = False
            if line.product_id:
                supplierinfo = line.product_id._select_customerinfo(
                    partner=line.partner_id, quantity=None
                )
                if supplierinfo:
                    code = supplierinfo.product_code or line.product_id.default_code
                    name = supplierinfo.product_name or line.product_id.name
                    customer_reference = "[%s] %s" % (code, name)
            line.product_customer_reference = customer_reference

    @api.onchange("product_id", "original_uom_qty")
    def onchange_product(self):
        if hasattr(super(), "onchange_product"):
            super().onchange_product()
        for line in self.filtered(
            lambda sbol: (
                sbol.product_id.product_tmpl_id.customer_ids
                and sbol.order_id.pricelist_id.item_ids
            )
        ):
            product = line.product_id
            items = self.env["product.pricelist.item"].search(
                [
                    ("pricelist_id", "=", line.order_id.pricelist_id.id),
                    ("compute_price", "=", "formula"),
                    ("base", "=", "partner"),
                    "|",
                    ("applied_on", "=", "3_global"),
                    "|",
                    "&",
                    ("categ_id", "=", product.categ_id.id),
                    ("applied_on", "=", "2_product_category"),
                    "|",
                    "&",
                    ("product_tmpl_id", "=", product.product_tmpl_id.id),
                    ("applied_on", "=", "1_product"),
                    "&",
                    ("product_id", "=", product.id),
                    ("applied_on", "=", "0_product_variant"),
                ]
            )
            if items:
                supplierinfo = line.product_id._select_customerinfo(
                    partner=line.partner_id, quantity=None
                )
                if supplierinfo and supplierinfo.min_qty:
                    line.original_uom_qty = supplierinfo.min_qty
