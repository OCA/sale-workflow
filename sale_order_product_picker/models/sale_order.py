# Copyright 2023 Tecnativa - Sergio Teruel
# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from ast import literal_eval
from datetime import timedelta

from odoo import api, fields, models
from odoo.osv import expression
from odoo.tools import float_compare, ormcache


class SaleOrder(models.Model):
    _inherit = "sale.order"

    picker_ids = fields.One2many(
        comodel_name="sale.order.picker",
        inverse_name="order_id",
        compute="_compute_picker_ids",
        compute_sudo=True,
    )
    # Not stored fields, they are only used to filter picker products
    picker_filter = fields.Selection(
        selection="_list_product_picker_filters", string="Filter", store=False
    )
    picker_origin_data = fields.Selection(
        selection=[("sale_order", "Last sales")],
        store=False,
    )
    picker_price_origin = fields.Selection(
        selection=[("last_sale_price", "Last price")],
        store=False,
    )
    picker_only_available = fields.Boolean(string="Available", store=False)
    use_delivery_address = fields.Boolean(store=False, default=False)
    picker_product_attribute_value_id = fields.Many2one(
        comodel_name="product.attribute.value",
        string="Attribute value",
        help="Filter products by attribute value",
        store=False,
    )
    picker_order = fields.Selection(
        selection=[
            ("categ_id", "Category"),
        ],
        store=False,
    )
    product_name_search = fields.Char(string="Search product", store=False)

    @api.model
    def _list_product_picker_filters(self):
        action = self.env.ref(
            "sale_order_product_picker.product_normal_action_sell_picker"
        )
        product_filters = self.env["ir.filters"].search(
            [("model_id", "=", "product.product"), ("action_id", "=", action.id)]
        )
        return [(f.id, f.name) for f in product_filters]

    @ormcache()
    def _get_partner_picker_field(self):
        # HACK: To avoid installation error when get default value to be used in a
        # depends of a computed field
        if "sale_order_product_picker" in self.env.registry._init_modules and self.env[
            "ir.default"
        ].get("sale.order", "use_delivery_address"):
            return "partner_shipping_id"
        else:
            return "partner_id"

    def _get_picker_trigger_search_fields(self):
        return [
            self._get_partner_picker_field(),
            "warehouse_id",
            "picker_order",
            "picker_origin_data",
            "picker_filter",
            "picker_only_available",
            "picker_product_attribute_value_id",
            "product_name_search",
        ]

    def _get_product_picker_limit(self):
        return int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_order_product_picker.product_picker_limit", "40")
        )

    def _get_picker_product_domain(self):
        product_filter = self.env["ir.filters"].browse(self.picker_filter)
        # TODO: Improve to apply field view domain (Assortments)
        domain = [
            ("sale_ok", "=", True),
            "|",
            ("company_id", "=", False),
            ("company_id", "=", self.company_id.id),
        ]
        if self.picker_only_available:
            available_field = self.env["sale.order.picker"]._get_qty_available_field()
            domain = expression.AND([domain, [(available_field, ">", 0.0)]])
        if product_filter.domain:
            domain = expression.AND([domain, literal_eval(product_filter.domain)])
        if self.picker_product_attribute_value_id:
            # If attribute create variant then filter by variant attribute value
            # else filter by template attribute value
            if (
                self.picker_product_attribute_value_id.attribute_id.create_variant
                != "no_variant"
            ):
                attribute_field = (
                    "product_template_variant_value_ids.product_attribute_value_id"
                )
            else:
                attribute_field = "attribute_line_ids.value_ids"
            domain.append(
                (
                    attribute_field,
                    "=",
                    self.picker_product_attribute_value_id.id,
                )
            )
        return domain

    # TODO: Invalidate cache on product write if next line is uncommented
    # @ormcache("self.partner_id", "self.picker_filter", "self.product_name_search")
    def _get_picker_product_ids(self):
        # [2:] to avoid partner and picker_order fields
        if not self.partner_id or not any(
            self[f_name] for f_name in self._get_picker_trigger_search_fields()[2:]
        ):
            self.picker_ids = False
            return None
        available_field = self.env["sale.order.picker"]._get_qty_available_field()
        self = self.with_context(
            warehouse=self.warehouse_id.id,
            to_date=available_field == "virtual_available"
            and self.env["sale.order.picker"]._get_virtual_available_to_date(
                self.commitment_date
            )
            or None,
        )
        Product = self.env["product.product"]
        domain = self._get_picker_product_domain()
        order = self.picker_order or None
        if self.product_name_search:
            product_ids = Product._name_search(self.product_name_search, args=domain)
            # Research to sort _name_search ids instead of browse sorted
            if order:
                product_ids = Product.search(
                    [("id", "in", product_ids)], order=order
                ).ids
        else:
            product_ids = Product.search(domain, order=order).ids
        return product_ids

    # TODO: Use field list instead overwrite method
    def filter_picker_so_lines(self, picker_data):
        return self.order_line.filtered(
            lambda sol: sol.product_id.id == picker_data["product_id"][0]
        )

    @api.depends(lambda s: s._get_picker_trigger_search_fields())
    def _compute_picker_ids(self):
        for order in self:
            product_ids = order._get_picker_product_ids()
            if product_ids is None:
                order.picker_ids = False
                continue
            picker_data_list = getattr(
                # Force no display archived records due we are in a computed method.
                # See: https://github.com/odoo/odoo/blob/
                # b1f9b7167979aa3a1910fd2ab09507eb26bd1f79/odoo/models.py#L6028
                order.with_context(active_test=True),
                "_get_product_picker_data_{}".format(
                    order.picker_origin_data or "products"
                ),
            )()
            picker_ids = self.env["sale.order.picker"].browse()
            for picker_data in picker_data_list:
                so_lines = order.filter_picker_so_lines(picker_data)
                picker_ids += order.picker_ids.new(
                    order._prepare_product_picker_vals(picker_data, so_lines)
                )
            order.picker_ids = picker_ids

    def _product_picker_data_sale_order_domain(self):
        """Domain to find recent SO lines."""
        months = 6
        start = fields.datetime.now() - timedelta(days=months * 30)
        start = fields.Datetime.to_string(start)
        partner = (
            self.partner_shipping_id
            if self.use_delivery_address
            else self.partner_id.commercial_partner_id
        )
        sale_order_partner_field = (
            "partner_shipping_id" if self.use_delivery_address else "partner_id"
        )
        # Search with sudo for get sale order from other commercials users
        other_sales = self.env["sale.order"].search(
            [
                ("company_id", "=", self.company_id.id),
                (sale_order_partner_field, "child_of", partner.id),
                ("date_order", ">=", start),
            ]
        )
        domain = [
            ("order_id", "in", (other_sales - self).ids),
            ("product_id", "in", self._get_picker_product_ids()),
            ("qty_delivered", "!=", 0.0),
        ]
        return domain

    def _prepare_product_picker_vals(self, group_line, so_lines):
        """Return the vals dictionary for creating a new recommendation line.
        @param group_line: Dictionary returned by the read_group operation.
        @param so_lines: Optional sales order line
        """
        discounts = set(so_lines.filtered("discount").mapped("discount"))
        vals = {
            "order_id": self.id,
            "sale_line_id": so_lines[:1].id,
            "product_id": group_line["product_id"][0],
            "is_in_order": bool(so_lines),
            "product_uom_qty": sum(so_lines.mapped("product_uom_qty")),
            "qty_delivered": group_line.get("qty_delivered", 0),
            "times_delivered": group_line.get("__count", 0),
            "discount": discounts.pop() if len(discounts) == 1 else 0,
            "multiple_discounts": not len(discounts) <= 1,
        }
        return vals

    def _get_product_picker_data_products(self):
        limit = self._get_product_picker_limit()
        products = self.env["product.product"].browse(
            self._get_picker_product_ids()[:limit]
        )
        return [{"product_id": (p.id, p.name)} for p in products]

    def _get_product_picker_data_sale_order(self):
        limit = self._get_product_picker_limit()
        if self.picker_order == "categ_id":
            found_lines = self.env["sale.order.line"].read_group(
                self._product_picker_data_sale_order_domain(),
                ["product_id", "categ_id", "qty_delivered"],
                ["product_id", "categ_id"],
                lazy=False,
            )
            found_lines = sorted(found_lines, key=lambda res: res["categ_id"][0])
        else:
            found_lines = self.env["sale.order.line"].read_group(
                self._product_picker_data_sale_order_domain(),
                ["product_id", "qty_delivered"],
                ["product_id"],
                lazy=False,
            )
            # Manual ordering that circumvents ORM limitations
            found_lines = sorted(
                found_lines,
                key=lambda res: (
                    res["__count"],
                    res["qty_delivered"],
                ),
                reverse=True,
            )
        return found_lines[:limit]


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    list_price = fields.Float(related="product_id.list_price")
    is_different_price = fields.Boolean(compute="_compute_is_different_price")
    categ_id = fields.Many2one(
        "product.category", related="product_id.categ_id", store=True
    )

    @api.depends("list_price", "price_unit")
    def _compute_is_different_price(self):
        digits = self.env["decimal.precision"].precision_get("Product Price")
        for line in self:
            line.is_different_price = (
                float_compare(line.price_unit, line.list_price, precision_digits=digits)
                == -1
            )
