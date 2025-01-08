from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    need_recompute_pricelist_global = fields.Boolean()
    has_pricelist_global = fields.Boolean(compute="_compute_has_pricelist_global")

    def _get_cummulative_quantity(self):
        """Compute the cummulative quantity of products in the sale order.
        :returns: dict{
            by_template: {product.template: qty},
            by_categ: {product.category: qty}}
        }
        """
        self.ensure_one()
        qty_data = {
            "by_template": {},
            "by_categ": {},
        }
        for line in self.order_line.filtered("product_id"):
            qty_in_product_uom = line.product_uom_qty
            # Final unit price is computed
            # according to `qty` in the default `uom_id`.
            if line.product_uom != line.product_id.uom_id:
                qty_in_product_uom = line.product_uom._compute_quantity(
                    qty_in_product_uom, line.product_id.uom_id
                )
            key_template = line.product_id.product_tmpl_id
            key_categ = line.product_id.categ_id
            qty_data["by_template"].setdefault(key_template, 0.0)
            qty_data["by_template"][key_template] += qty_in_product_uom
            qty_data["by_categ"].setdefault(key_categ, 0.0)
            qty_data["by_categ"][key_categ] += qty_in_product_uom
        return qty_data

    @api.depends("pricelist_id")
    def _compute_has_pricelist_global(self):
        for sale in self:
            if not sale.pricelist_id:
                sale.has_pricelist_global = False
                continue
            qty_data = self._get_cummulative_quantity()
            pricelist = sale.pricelist_id.with_context(
                pricelist_global_cummulative_quantity=qty_data
            )
            suitable_rule = self.env["product.pricelist.item"]
            for line in sale.order_line:
                suitable_rule = pricelist._get_product_rule(
                    line.product_id,
                    quantity=line.product_uom_qty or 1.0,
                    uom=line.product_uom,
                    date=line.order_id.date_order,
                )
                if suitable_rule:
                    break
            sale.has_pricelist_global = bool(suitable_rule)

    @api.onchange("order_line")
    def _onchange_need_recompute_pricelist_global(self):
        self.need_recompute_pricelist_global = True

    def button_compute_pricelist_global_rule(self):
        self.ensure_one()
        # Clear existing discounts before recomputing.
        self.order_line.write({"discount": 0.0})
        qty_data = self._get_cummulative_quantity()
        sale_order = self.with_context(pricelist_global_cummulative_quantity=qty_data)
        sale_order.order_line._compute_pricelist_item_id()
        sale_order.order_line._compute_price_unit()
        sale_order.order_line._compute_discount()
        self.need_recompute_pricelist_global = False
