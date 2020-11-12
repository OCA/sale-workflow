from odoo import _, api, fields, models
from odoo.exceptions import Warning as OdooWarning


class TieredPricingWizard(models.TransientModel):
    """Allows the user to create tiered items for the current product (or variant).
       We can get to here from the product template view, variant view, or elsewhere.
       The idea is to fill the information from variants if we come from variants,
       and use defaults otherwise.
    """

    _name = "product.tiered_pricing.wizard"
    _description = "Wizard to automatically set tiered pricing on products."

    @api.model
    def _get_record_from_context(self, model):
        """Returns a record if active_ids is set in context together with active_model.
        """
        record = self.env[model]
        if self.env.context.get("active_model") == model:
            active_ids = self.env.context.get("active_ids")
            record_id = active_ids[0] if active_ids else None
            if record_id:
                record = record.browse(record_id)
        return record

    @api.model
    def _default_product_template(self):
        """The template that can be extracted from context, or first one in db."""
        template = None
        active_model = self.env.context.get("active_model")
        if active_model == "product.template":
            template = self._get_record_from_context("product.template")
        elif active_model == "product.product":
            template = self._get_record_from_context("product.product").product_tmpl_id
        return template or self.env["product.template"].search([], limit=1)

    def _in_variant_context(self):
        return self.env.context.get("active_model") == "product.product"

    @api.model
    def _default_tiered_pricing(self):
        domain = [("is_tiered_pricing", "=", True)]
        return self.env["product.pricelist"].search(domain, limit=1)

    @api.onchange("product_template_id")
    def onchange_product_template_id(self):
        self.variant_ids = self.product_template_id.valid_existing_variant_ids
        if self._in_variant_context() and self.only_variants:
            context_variant = self._get_record_from_context("product.product")
            if self.product_template_id == context_variant.product_tmpl_id:
                self.variant_ids = context_variant
        return {}

    product_template_id = fields.Many2one(
        "product.template", string="Product", default=_default_product_template
    )
    only_variants = fields.Boolean("Restrict to variants", default=_in_variant_context)
    variant_ids = fields.Many2many("product.product", string="Variants")
    pricelist_ids = fields.Many2many(
        "product.pricelist",
        string="Pricelists where items will be created",
        domain=[("is_tiered_pricing", "=", False)],
        required=True,
    )
    tiered_pricing_id = fields.Many2one(
        "product.pricelist",
        string="Tiered Pricing",
        default=_default_tiered_pricing,
        domain=[("is_tiered_pricing", "=", True)],
    )

    def create_pricelist_items(self):
        if not self.pricelist_ids:
            raise OdooWarning(_("You should select at least one target pricelist!"))
        if not self.only_variants and not self.product_template_id:
            raise OdooWarning(_("You should select a product!"))
        if self.only_variants and not self.variant_ids:
            raise OdooWarning(_("You should select at least one variant!"))

        item_values = {
            "compute_price": "tier",
            "tiered_pricelist_id": self.tiered_pricing_id.id,
            "applied_on": "0_product_variant" if self.only_variants else "1_product",
        }
        if self.only_variants:
            for variant in self.variant_ids:
                item_values["product_id"] = variant.id
                self._find_or_create_item(item_values)
        else:
            item_values["product_tmpl_id"] = self.product_template_id.id
            self._find_or_create_item(item_values)

        return {"type": "ir.actions.act_window_close"}

    def _find_or_create_item(self, item_values):
        for pricelist in self.pricelist_ids:
            Items = self.env["product.pricelist.item"]
            pricelist_item_values = {**item_values, "pricelist_id": pricelist.id}
            existing_item = Items.search(self.values_to_domain(pricelist_item_values))
            if not existing_item:
                Items.create(pricelist_item_values)

    def values_to_domain(self, values):
        domain = []
        for key in values:
            domain.append((key, "=", values[key]))
        return domain
