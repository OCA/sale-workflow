from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    def _compute_price_rule_get_items(
        self, products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids
    ):
        items = super()._compute_price_rule_get_items(
            products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids
        )
        # ignore new global rules on Odoo standard
        return items.filtered(
            lambda item: item.applied_on
            not in ["4_global_product_template", "5_global_product_category"]
        )

    def _compute_price_rule_get_items_globals(self, date, prod_tmpl_ids, categ_ids):
        self.ensure_one()
        # Load all global rules
        # inspired by _compute_price_rule_get_items
        # but only for global rules
        self.env["product.pricelist.item"].flush(
            ["price", "currency_id", "company_id", "active", "date_start", "date_end"]
        )
        self.env.cr.execute(
            """
            SELECT
                item.id
            FROM
                product_pricelist_item AS item
            LEFT JOIN product_category AS categ
                ON item.global_categ_id = categ.id
            WHERE
                (item.global_product_tmpl_id IS NULL OR item.global_product_tmpl_id = any(%s))
                AND (item.global_categ_id IS NULL OR item.global_categ_id = any(%s))
                AND (item.pricelist_id = %s)
                AND (item.date_start IS NULL OR item.date_start<=%s)
                AND (item.date_end IS NULL OR item.date_end>=%s)
                AND (item.active = TRUE)
                AND item.applied_on IN (
                    '4_global_product_template',
                    '5_global_product_category'
                )
            ORDER BY
                item.applied_on, item.min_quantity desc, categ.complete_name desc, item.id desc
            """,
            (prod_tmpl_ids, categ_ids, self.id, date, date),
        )
        # NOTE: if you change `order by` on that query, make sure it matches
        # _order from model to avoid inconstencies and undeterministic issues.

        item_ids = [x[0] for x in self.env.cr.fetchall()]
        return self.env["product.pricelist.item"].browse(item_ids)

    def _extract_products_and_categs_from_sale(self, sale):
        """
        Extract unique product templates and categories (including their parents)
        :param sale: browse_record(sale.order)
        :returns: tuple(product_template_ids , product_category_ids)
        """
        categ_ids = set()
        prod_tmpl_ids = set()
        for line in sale.order_line.filtered(lambda x: not x.display_type):
            prod_tmpl_ids.add(line.product_id.product_tmpl_id.id)
            categ = line.product_id.categ_id
            while categ:
                categ_ids.add(categ.id)
                categ = categ.parent_id
        return list(prod_tmpl_ids), list(categ_ids)

    def _compute_price_rule_global(self, sale):
        """Compute the price for the given sale order
        :param sale: browse_record(sale.order)
        :returns: dict{sale_order_line_id: (price, suitable_rule) for the given pricelist}
        """
        self.ensure_one()
        date = sale.date_order
        qty_data = {
            "by_template": {},
            "by_categ": {},
        }
        for line in sale.order_line.filtered(lambda x: not x.display_type):
            qty_in_product_uom = line.product_uom_qty
            # Final unit price is computed according to `qty` in the default `uom_id`.
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

        prod_tmpl_ids, categ_ids = self._extract_products_and_categs_from_sale(sale)

        items = self._compute_price_rule_get_items_globals(
            date, prod_tmpl_ids, categ_ids
        )
        results = {}
        for line in sale.order_line.filtered(lambda x: not x.display_type):
            product = line.product_id
            results[line.id] = 0.0
            suitable_rule = False

            # if Public user try to access standard price from website sale,
            # need to call price_compute.
            price = product.price_compute("list_price")[product.id]

            price_uom = product.uom_id
            for rule in items:
                if not rule._is_applicable_for_sale(product.product_tmpl_id, qty_data):
                    continue
                if rule.base == "pricelist" and rule.base_pricelist_id:
                    # first, try compute the price for global rule
                    # otherwise, fallback to regular computation
                    # with qty from line instead of accumulated qty
                    (
                        price,
                        rule_applied,
                    ) = rule.base_pricelist_id._compute_price_rule_global(sale)[line.id]
                    if not rule_applied:
                        price = rule.base_pricelist_id._compute_price_rule(
                            [(product, line.product_uom_qty, sale.partner_id)],
                            date,
                            line.product_uom.id,
                        )[product.id][0]
                    src_currency = rule.base_pricelist_id.currency_id
                else:
                    # if base option is public price take sale price else cost price of product
                    # price_compute returns the price in the context UoM, i.e. qty_uom_id
                    price = product.price_compute(rule.base)[product.id]
                    if rule.base == "standard_price":
                        src_currency = product.cost_currency_id
                    else:
                        src_currency = product.currency_id

                if src_currency != self.currency_id:
                    price = src_currency._convert(
                        price, self.currency_id, self.env.company, date, round=False
                    )

                if price is not False:
                    price = rule._compute_price(price, price_uom, product)
                    suitable_rule = rule
                break

            if not suitable_rule:
                cur = product.currency_id
                price = cur._convert(
                    price, self.currency_id, self.env.company, date, round=False
                )

            results[line.id] = (price, suitable_rule and suitable_rule.id or False)

        return results


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    applied_on = fields.Selection(
        selection_add=[
            ("4_global_product_template", "Global - Product template"),
            ("5_global_product_category", "Global - Product category"),
        ],
        ondelete={
            "4_global_product_template": "set default",
            "5_global_product_category": "set default",
        },
    )
    global_product_tmpl_id = fields.Many2one(
        "product.template",
        "Product",
        ondelete="cascade",
        check_company=True,
    )
    global_categ_id = fields.Many2one(
        "product.category",
        "Product Category",
        ondelete="cascade",
    )

    @api.constrains(
        "product_id",
        "product_tmpl_id",
        "categ_id",
        "global_product_tmpl_id",
        "global_categ_id",
    )
    def _check_product_consistency(self):
        res = super()._check_product_consistency()
        for item in self:
            if (
                item.applied_on == "5_global_product_category"
                and not item.global_categ_id
            ):
                raise ValidationError(
                    _(
                        "Please specify the category "
                        "for which this global rule should be applied"
                    )
                )
            elif (
                item.applied_on == "4_global_product_template"
                and not item.global_product_tmpl_id
            ):
                raise ValidationError(
                    _(
                        "Please specify the product "
                        "for which this global rule should be applied"
                    )
                )
        return res

    @api.depends(
        "applied_on",
        "categ_id",
        "product_tmpl_id",
        "product_id",
        "global_product_tmpl_id",
        "global_categ_id",
        "compute_price",
        "fixed_price",
        "pricelist_id",
        "percent_price",
        "price_discount",
        "price_surcharge",
    )
    def _get_pricelist_item_name_price(self):
        res = super()._get_pricelist_item_name_price()
        for item in self:
            if item.global_categ_id and item.applied_on == "5_global_product_category":
                item.name = _("Global category: %s") % (
                    item.global_categ_id.display_name
                )
            elif (
                item.global_product_tmpl_id
                and item.applied_on == "4_global_product_template"
            ):
                item.name = _("Global product: %s") % (
                    item.global_product_tmpl_id.display_name
                )
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get("applied_on", False):
                # Ensure item consistency for later searches.
                applied_on = values["applied_on"]
                if applied_on == "5_global_product_category":
                    values.update(
                        {
                            "product_id": None,
                            "product_tmpl_id": None,
                            "categ_id": None,
                            "global_product_tmpl_id": None,
                        }
                    )
                elif applied_on == "4_global_product_template":
                    values.update(
                        {
                            "product_id": None,
                            "product_tmpl_id": None,
                            "categ_id": None,
                            "global_categ_id": None,
                        }
                    )
        return super().create(vals_list)

    def write(self, values):
        if values.get("applied_on", False):
            # Ensure item consistency for later searches.
            applied_on = values["applied_on"]
            if applied_on == "5_global_product_category":
                values.update(
                    {
                        "product_id": None,
                        "product_tmpl_id": None,
                        "categ_id": None,
                        "global_product_tmpl_id": None,
                    }
                )
            elif applied_on == "4_global_product_template":
                values.update(
                    {
                        "product_id": None,
                        "product_tmpl_id": None,
                        "categ_id": None,
                        "global_categ_id": None,
                    }
                )
        return super().write(values)

    def _is_applicable_for_sale(self, product_template, qty_data):
        """Check whether the current rule is valid
        for the given sale order and cummulated quantity.
        :param product_template: browse_record(product.template)
        :param qty_data:
            dict{
                by_categ: dict{record<product.categ>: qty, ...},
                by_template: dict{record<product.template>: qty, ...}
            }
        :returns: Whether rules is valid or not
        :rtype: bool
        """
        self.ensure_one()
        is_applicable = True
        if self.applied_on == "4_global_product_template":
            total_qty = qty_data["by_template"].get(product_template, 0.0)
            if self.min_quantity and total_qty < self.min_quantity:
                is_applicable = False
            elif self.global_product_tmpl_id != product_template:
                is_applicable = False
        elif self.applied_on == "5_global_product_category":
            total_qty = qty_data["by_categ"].get(product_template.categ_id, 0.0)
            if self.min_quantity and total_qty < self.min_quantity:
                is_applicable = False
            elif not product_template.categ_id.parent_path.startswith(
                self.global_categ_id.parent_path
            ):
                is_applicable = False
        return is_applicable
