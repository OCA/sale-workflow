# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    rfq_ids = fields.One2many(
        "purchase.order",
        "sale_quotation_id",
        string="RFQs",
        help="RFQs created from this sale order",
    )
    rfq_count = fields.Integer(
        string="RFQ count",
        compute="_compute_rfq_count",
        help="Number of RFQ created from this sale order",
    )

    @api.depends("rfq_ids")
    def _compute_rfq_count(self):
        """
        Compute the number of RFQs created from this sale order
        """
        for order in self:
            order.rfq_count = len(order.rfq_ids)

    def action_view_rfq(self):
        """
        View the purchase orders created from this sale order
        """
        self.ensure_one()
        action = self.env.ref("purchase.purchase_rfq").sudo().read()[0]
        action["domain"] = [("id", "in", self.rfq_ids.ids)]
        return action

    def action_create_rfq(self):
        """
        Create purchase orders from this sale order
        """
        self.ensure_one()
        self._create_rfq()
        if self.rfq_count:
            return self.action_view_rfq()
        raise UserError(_("No RFQs created"))

    def _get_capable_vendors(self, days_min=0, days_max=0):
        """
        Returns a recordset of res.partner records that match the criteria

        :param days_min: Minimum delivery time to match
        :param days_max: Maximum delivery time to match

        return: Recordset of res.partner
        """
        self.ensure_one()
        vendors_dict = self._get_vendor_dict(days_min, days_max)
        return vendors_dict.keys()

    def _create_rfq(self):
        """
        Create purchase orders from this sale order
        """
        self.ensure_one()
        vendors_dict = self._get_vendor_dict()
        for vendor, value in vendors_dict.items():
            purchase = self.env["purchase.order"].create(self._prepare_rfq_vals(vendor))
            for line in value:
                self.env["purchase.order.line"].create(
                    self._prepare_rfq_line_vals(purchase, line)
                )
        self._added_alternative_rfq()

    def _prepare_rfq_vals(self, vendor):
        """
        Prepare values for purchase.order

        :param vendor: res.partner

        :return: dict
        """
        return {
            "partner_id": vendor.id,
            "origin": self.name,
            "sale_quotation_id": self.id,
            "currency_id": self.currency_id.id,
            "company_id": self.company_id.id,
        }

    def _prepare_rfq_line_vals(self, rfq, line):
        """
        Prepare values for purchase.order.line

        :param rfq: purchase.order
        :param line: dict

        :return: dict
        """
        return {
            "order_id": rfq.id,
            "product_id": line["line"].product_id.id,
            "name": line["line"].name,
            "product_qty": line["line"].product_uom_qty,
            "product_uom": line["line"].product_uom.id,
            "price_unit": line["supplierinfo"].currency_id._convert(
                line["supplierinfo"].price,
                rfq.currency_id,
                self.env.company,
                fields.Date.today(),
            ),
            "date_planned": fields.Datetime.now(),
        }

    def _get_vendor_dict(self, days_min=0, days_max=0):
        """
        Returns a dict of res.partner records that match the criteria

        :param days_min: Minimum delivery time to match
        :param days_max: Maximum delivery time to match

        :return: dict
        """
        vendors_dict = defaultdict(list)
        for line in self.order_line:
            supplierinfos = line.product_id._get_matching_vendor_pricelists(
                line.product_uom_qty, days_min, days_max
            )
            for supplierinfo in supplierinfos:
                vals = {
                    "supplierinfo": supplierinfo,
                    "line": line,
                }
                vendors_dict[supplierinfo.partner_id].append(vals)
        return vendors_dict

    def _convert_to_currency(self, price, currency_id, currency_to_id):
        """
        Convert price to currency

        :param price: float
        :param currency_id: res.currency
        :param currency_to_id: res.currency

        :return: float
        """
        if currency_id != currency_to_id:
            price = currency_id._convert(
                price, currency_to_id, self.env.company, fields.Date.today()
            )
        return price

    def _added_alternative_rfq(self):
        """
        Added alternative RFQ
        """
        self.ensure_one()
        if len(self.rfq_ids) <= 1:
            return
        self.rfq_ids.write(
            {
                "purchase_group_id": self.env["purchase.order.group"].create({}).id,
            }
        )
