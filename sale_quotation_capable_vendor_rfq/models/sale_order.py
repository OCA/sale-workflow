# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    purchase_order_ids = fields.One2many(
        "purchase.order",
        "sale_order_id",
        string="Purchase Orders",
        help="Purchase orders created from this sale order",
    )
    purchase_count = fields.Integer(
        string="Purchase Orders",
        compute="_compute_purchase_count",
        help="Number of purchase orders created from this sale order",
    )

    @api.depends("purchase_order_ids")
    def _compute_purchase_count(self):
        """
        Compute the number of RFQs created from this sale order
        """
        for order in self:
            order.purchase_count = len(order.purchase_order_ids)

    def action_view_purchase_orders(self):
        """
        View the purchase orders created from this sale order
        """
        self.ensure_one()
        action = self.env.ref("purchase.purchase_rfq").read()[0]
        action["domain"] = [("id", "in", self.purchase_order_ids.ids)]
        return action

    def action_create_purchase_orders(self):
        """
        Create purchase orders from this sale order
        """
        self.ensure_one()
        self._create_purchase_orders()
        if self.purchase_count:
            return self.action_view_purchase_orders()
        return True

    def _get_capable_vendors(self, lead_time=0):
        """
        Returns a recordset of res.partner records that match the criteria

        param lead_time: Integer of days to match

        return: Recordset of res.partner
        """
        self.ensure_one()
        vendors_dict = self._get_vendor_dict(lead_time)
        return vendors_dict.keys()

    def _create_purchase_orders(self):
        """
        Create purchase orders from this sale order
        """
        self.ensure_one()
        vendors_dict = self._get_vendor_dict()
        for vendor, value in vendors_dict.items():
            vals_purchase = {
                "partner_id": vendor.id,
                "origin": self.name,
                "sale_order_id": self.id,
                "currency_id": self.currency_id.id,
                "company_id": self.company_id.id,
            }
            purchase = self.env["purchase.order"].create(vals_purchase)
            for line in value:
                vals_purchase_line = {
                    "order_id": purchase.id,
                    "product_id": line["line"].product_id.id,
                    "name": line["line"].name,
                    "product_qty": line["line"].product_uom_qty,
                    "product_uom": line["line"].product_uom.id,
                    "price_unit": self._convert_to_currency(
                        line["supplierinfo"].price,
                        line["supplierinfo"].currency_id,
                        purchase.currency_id,
                    ),
                    "date_planned": fields.Datetime.now(),
                }
                self.env["purchase.order.line"].create(vals_purchase_line)

    def _get_vendor_dict(self, lead_time=0):
        vendors_dict = {}
        for line in self.order_line:
            supplierinfo_ids = line.product_id._get_matching_vendor_pricelists(
                line.product_uom_qty, lead_time
            )
            for supplierinfo in supplierinfo_ids:
                vals = {
                    "supplierinfo": supplierinfo,
                    "line": line,
                }
                if supplierinfo.partner_id not in vendors_dict:
                    vendors_dict[supplierinfo.partner_id] = [vals]
                else:
                    vendors_dict[supplierinfo.partner_id].append(vals)
        return vendors_dict

    def _convert_to_currency(self, price, currency_id, currency_to_id):
        """
        Convert price to currency
        """
        if currency_id != currency_to_id:
            price = currency_id._convert(
                price, currency_to_id, self.env.company, fields.Date.today()
            )
        return price
