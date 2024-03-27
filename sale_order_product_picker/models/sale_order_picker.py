# Copyright 2023 Tecnativa - Sergio Teruel
# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from datetime import datetime, time

from odoo import api, fields, models
from odoo.tools import float_compare, ormcache


class SaleOrderPicker(models.Model):
    _name = "sale.order.picker"
    _description = "sale.order.picker"

    order_id = fields.Many2one(comodel_name="sale.order")
    product_id = fields.Many2one(comodel_name="product.product")
    product_image = fields.Image(related="product_id.image_256")
    sale_line_id = fields.Many2one(comodel_name="sale.order.line")
    is_in_order = fields.Boolean()
    product_uom_qty = fields.Float(string="Quantity", digits="Product Unit of Measure")
    uom_id = fields.Many2one(comodel_name="uom.uom", related="product_id.uom_id")
    unit_name = fields.Char(compute="_compute_unit_name")
    qty_available = fields.Float(
        string="On Hand",
        digits="Product Unit of Measure",
        compute="_compute_qty_available",
    )
    qty_delivered = fields.Float(string="Delivered", digits="Product Unit of Measure")
    times_delivered = fields.Integer()
    price_unit = fields.Float(
        string="Unit Price", compute="_compute_price_unit", digits="Product Price"
    )
    category_id = fields.Many2one("product.category", related="product_id.categ_id")
    currency_id = fields.Many2one(related="order_id.currency_id", depends=["order_id"])
    list_price = fields.Float(related="product_id.list_price")
    is_different_price = fields.Boolean(compute="_compute_is_different_price")
    discount = fields.Float(string="Discount (%)", digits="Discount")
    multiple_discounts = fields.Boolean()
    line_price_reduce = fields.Float()
    warehouse_id = fields.Many2one("stock.warehouse", compute="_compute_warehouse_id")
    pricelist_item_id = fields.Many2one(
        "product.pricelist.item", compute="_compute_pricelist_item_id"
    )
    product_no_variant_attribute_value_ids = fields.Many2many(
        comodel_name="product.template.attribute.value",
        string="Extra Values",
        compute="_compute_no_variant_attribute_values",
        store=True,
        readonly=False,
        precompute=True,
        ondelete="restrict",
    )
    compute_price_unit = fields.Boolean(store=False)

    @api.depends("product_id", "warehouse_id")
    def _compute_warehouse_id(self):
        for line in self:
            line.warehouse_id = line.order_id.warehouse_id

    @api.depends("product_id", "uom_id", "product_uom_qty")
    def _compute_pricelist_item_id(self):
        for line in self:
            if not line.order_id.pricelist_id:
                line.pricelist_item_id = False
            else:
                line.pricelist_item_id = line.order_id.pricelist_id._get_product_rule(
                    line.product_id,
                    line.product_uom_qty or 1.0,
                    uom=line.uom_id,
                    date=line.order_id.date_order,
                )

    @api.depends("product_id")
    def _compute_no_variant_attribute_values(self):
        for line in self:
            if not line.product_id:
                line.product_no_variant_attribute_value_ids = False
                continue
            if not line.product_no_variant_attribute_value_ids:
                continue
            prod = line.product_id.product_tmpl_id
            valid_values = (
                prod.valid_product_template_attribute_line_ids.product_template_value_ids
            )
            for ptav in line.product_no_variant_attribute_value_ids:
                if ptav._origin not in valid_values:
                    line.product_no_variant_attribute_value_ids -= ptav

    def _get_picker_price_unit_context(self):
        return {
            "partner": self.order_id.partner_id,
            "pricelist": self.order_id.pricelist_id.id,
            "quantity": self.product_uom_qty,
        }

    @api.depends(
        "product_id",
        "order_id.partner_id",
        "order_id.picker_price_origin",
        "compute_price_unit",
    )
    def _compute_price_unit(self):
        """
        Get product price unit from product list price or from last sale price
        """
        sale_order = fields.first(self).order_id
        price_origin = sale_order.picker_price_origin or "pricelist"
        use_delivery_address = sale_order.use_delivery_address
        for line in self:
            if line.sale_line_id:
                line.price_unit = line.sale_line_id.price_unit
                line.discount = line.sale_line_id.discount
                line.line_price_reduce = line.sale_line_id.price_reduce
            elif price_origin == "last_sale_price":
                (
                    line.price_unit,
                    line.discount,
                    line.line_price_reduce,
                ) = line._get_last_sale_price_product(use_delivery_address)
            else:
                (
                    line.price_unit,
                    line.discount,
                    line.line_price_reduce,
                ) = line.get_display_price()

    def get_display_price(self):
        self.ensure_one()
        discount_to_apply = 0.0
        new_list_price = 0.0
        price = self._get_pricelist_price()
        if self.order_id.pricelist_id.discount_policy == "without_discount":
            new_list_price = self._get_pricelist_price_before_discount()
            if new_list_price != 0:
                discount = (new_list_price - price) / new_list_price * 100
                if (discount > 0 and new_list_price > 0) or (
                    discount < 0 and new_list_price < 0
                ):
                    discount_to_apply = discount
        return new_list_price or price, discount_to_apply, price

    def _get_pricelist_price(self):
        self.ensure_one()
        self.product_id.ensure_one()
        pricelist_rule = self.pricelist_item_id
        order_date = self.order_id.date_order or fields.Date.today()
        product = self.product_id.with_context(**self._get_product_price_context())
        qty = self.product_uom_qty or 1.0
        uom = self.uom_id or self.product_id.uom_id
        currency = self.currency_id or self.order_id.company_id.currency_id
        return pricelist_rule._compute_price(
            product, qty, uom, order_date, currency=currency
        )

    def _get_product_price_context(self):
        self.ensure_one()
        res = {}
        no_variant_attributes_price_extra = [
            ptav.price_extra
            for ptav in self.product_no_variant_attribute_value_ids.filtered(
                lambda ptav: ptav.price_extra
                and ptav not in self.product_id.product_template_attribute_value_ids
            )
        ]
        if no_variant_attributes_price_extra:
            res["no_variant_attributes_price_extra"] = tuple(
                no_variant_attributes_price_extra
            )
        return res

    def _get_pricelist_price_before_discount(self):
        self.ensure_one()
        self.product_id.ensure_one()
        pricelist_rule = self.pricelist_item_id
        order_date = self.order_id.date_order or fields.Date.today()
        product = self.product_id.with_context(**self._get_product_price_context())
        qty = self.product_uom_qty or 1.0
        uom = self.uom_id or self.product_id.uom_id
        if pricelist_rule:
            pricelist_item = pricelist_rule
            if pricelist_item.pricelist_id.discount_policy == "without_discount":
                while (
                    pricelist_item.base == "pricelist"
                    and pricelist_item.base_pricelist_id.discount_policy
                    == "without_discount"
                ):
                    rule_id = pricelist_item.base_pricelist_id._get_product_rule(
                        product, qty, uom=uom, date=order_date
                    )
                    pricelist_item = self.env["product.pricelist.item"].browse(rule_id)
            pricelist_rule = pricelist_item
        return pricelist_rule._compute_base_price(
            product,
            qty,
            uom,
            order_date,
            target_currency=self.currency_id,
        )

    @api.model
    def _get_qty_available_field(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "sale_order_product_picker.product_available_field", "qty_available"
            )
        )

    @api.model
    @ormcache()
    def _get_virtual_available_time(self):
        """
        Returns a tuple containing the hour and minute from product_virtual_available_time
        system parameter.
        """
        virtual_available_time = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_order_product_picker.product_virtual_available_time")
        )
        hour = minute = None
        if virtual_available_time:
            split_time = virtual_available_time.split(":")
            hour = int(split_time[0])
            minute = int(split_time[1])
        return hour, minute

    @api.model
    def _get_virtual_available_to_date(self, commitment_date=None):
        """
        Return the virtual available date up to the specified commitment date, or today's
        date if no commitment date is provided.
        """
        to_date = commitment_date or fields.Date.today()
        hour, minute = self._get_virtual_available_time()
        if hour is not None:
            to_date = datetime.combine(
                to_date, time(hour=hour, minute=minute, second=59, microsecond=999999)
            )
        return to_date

    def _compute_qty_available(self):
        available_field = self._get_qty_available_field()
        self = self.with_context(
            warehouse=self.warehouse_id.id,
            to_date=available_field == "virtual_available"
            and self._get_virtual_available_to_date(self.order_id.commitment_date)
            or None,
        )
        for line in self:
            line.qty_available = line.product_id[available_field]

    def _get_last_sale_price_product(self, use_delivery_address=False):
        """
        Get last price from last order.
        Use sudo to read sale order from other users like as other commercials.
        """
        self.ensure_one()
        domain = [
            ("company_id", "=", self.order_id.company_id.id),
            ("state", "not in", ("draft", "sent", "cancel")),
            ("product_id", "=", self.product_id.id),
        ]
        if use_delivery_address:
            domain.append(
                (
                    "order_id.partner_shipping_id",
                    "child_of",
                    self.order_id.partner_shipping_id.id,
                )
            )
        else:
            domain.append(
                (
                    "order_partner_id",
                    "child_of",
                    self.order_id.partner_id.commercial_partner_id.id,
                )
            )
        so_line = (
            self.env["sale.order.line"]
            .sudo()
            .search(
                domain,
                limit=1,
                order="id DESC",
            )
            .with_context(prefetch_fields=False)
        )
        return so_line.price_unit, so_line.discount, so_line.price_reduce

    def add_to_cart(self):
        self.ensure_one()
        so_line = self.order_id.order_line.new({"product_id": self.product_id.id})
        self.order_id.order_line += so_line

    @api.depends("list_price", "price_unit", "line_price_reduce")
    def _compute_is_different_price(self):
        digits = self.env["decimal.precision"].precision_get("Product Price")
        for line in self:
            if line.line_price_reduce:
                line.is_different_price = (
                    float_compare(
                        line.line_price_reduce, line.list_price, precision_digits=digits
                    )
                    == -1
                )
            else:
                line.is_different_price = (
                    float_compare(
                        line.price_unit, line.list_price, precision_digits=digits
                    )
                    == -1
                )

    @api.depends("product_id")
    def _compute_unit_name(self):
        secondary_unit_installed = "sale_secondary_uom_id" in self.product_id._fields
        for line in self:
            if secondary_unit_installed and line.product_id.sale_secondary_uom_id:
                line.unit_name = line.product_id.sale_secondary_uom_id.display_name
            else:
                line.unit_name = line.product_id.uom_id.name
