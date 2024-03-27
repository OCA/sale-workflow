# Copyright 2019 Akretion
# Copyright 2024 CorporateHub
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

RESTRICTION_ENABLED = "1"
RESTRICTION_DISABLED = "0"
RESTRICTION_SELECTION = [
    (RESTRICTION_ENABLED, "Yes"),
    (RESTRICTION_DISABLED, "No"),
]


class ProductRestrictedQtyMixin(models.AbstractModel):
    _name = "product.restricted.qty.mixin"
    _description = "Product Restricted Qty Mixin"

    is_sale_own_min_qty_set = fields.Boolean()
    is_sale_inherited_min_qty_set = fields.Boolean(
        compute="_compute_is_sale_inherited_min_qty_set",
        recursive=True,
    )
    is_sale_min_qty_set = fields.Boolean(
        compute="_compute_is_sale_min_qty_set",
        recursive=True,
    )
    sale_own_min_qty = fields.Float(
        digits="Product Unit of Measure",
    )
    sale_inherited_min_qty = fields.Float(
        compute="_compute_sale_inherited_min_qty",
        digits="Product Unit of Measure",
        store=True,
        recursive=True,
    )
    sale_min_qty = fields.Float(
        help="The minimum quantity of product that can be sold.",
        compute="_compute_sale_min_qty",
        inverse="_inverse_sale_min_qty",
        store=True,
        recursive=True,
        digits="Product Unit of Measure",
    )

    is_sale_own_restrict_min_qty_set = fields.Boolean(
        compute="_compute_is_sale_own_restrict_min_qty_set",
        inverse="_inverse_is_sale_own_restrict_min_qty_set",
    )
    is_sale_inherited_restrict_min_qty_set = fields.Boolean(
        compute="_compute_is_sale_inherited_restrict_min_qty_set",
        recursive=True,
    )
    is_sale_restrict_min_qty_set = fields.Boolean(
        compute="_compute_is_sale_restrict_min_qty_set",
        recursive=True,
    )
    sale_own_restrict_min_qty = fields.Selection(
        selection=RESTRICTION_SELECTION,
    )
    sale_inherited_restrict_min_qty = fields.Selection(
        selection=RESTRICTION_SELECTION,
        compute="_compute_sale_inherited_restrict_min_qty",
        store=True,
        recursive=True,
    )
    sale_restrict_min_qty = fields.Selection(
        help="Enforce the minimum quantity of product that can be sold.",
        selection=RESTRICTION_SELECTION,
        compute="_compute_sale_restrict_min_qty",
        inverse="_inverse_sale_restrict_min_qty",
        store=True,
        recursive=True,
    )

    is_sale_own_max_qty_set = fields.Boolean()
    is_sale_inherited_max_qty_set = fields.Boolean(
        compute="_compute_is_sale_inherited_max_qty_set",
        recursive=True,
    )
    is_sale_max_qty_set = fields.Boolean(
        compute="_compute_is_sale_max_qty_set",
        recursive=True,
    )
    sale_own_max_qty = fields.Float(
        digits="Product Unit of Measure",
    )
    sale_inherited_max_qty = fields.Float(
        compute="_compute_sale_inherited_max_qty",
        digits="Product Unit of Measure",
        store=True,
        recursive=True,
    )
    sale_max_qty = fields.Float(
        help="The maximum quantity of product that can be sold.",
        compute="_compute_sale_max_qty",
        inverse="_inverse_sale_max_qty",
        store=True,
        recursive=True,
        digits="Product Unit of Measure",
    )

    is_sale_own_restrict_max_qty_set = fields.Boolean(
        compute="_compute_is_sale_own_restrict_max_qty_set",
        inverse="_inverse_is_sale_own_restrict_max_qty_set",
    )
    is_sale_inherited_restrict_max_qty_set = fields.Boolean(
        compute="_compute_is_sale_inherited_restrict_max_qty_set",
        recursive=True,
    )
    is_sale_restrict_max_qty_set = fields.Boolean(
        compute="_compute_is_sale_restrict_max_qty_set",
        recursive=True,
    )
    sale_own_restrict_max_qty = fields.Selection(
        selection=RESTRICTION_SELECTION,
    )
    sale_inherited_restrict_max_qty = fields.Selection(
        selection=RESTRICTION_SELECTION,
        compute="_compute_sale_inherited_restrict_max_qty",
        store=True,
        recursive=True,
    )
    sale_restrict_max_qty = fields.Selection(
        help="Enforce the maximum quantity of product that can be sold.",
        selection=RESTRICTION_SELECTION,
        compute="_compute_sale_restrict_max_qty",
        inverse="_inverse_sale_restrict_max_qty",
        store=True,
        recursive=True,
    )

    is_sale_own_multiple_of_qty_set = fields.Boolean()
    is_sale_inherited_multiple_of_qty_set = fields.Boolean(
        compute="_compute_is_sale_inherited_multiple_of_qty_set",
        recursive=True,
    )
    is_sale_multiple_of_qty_set = fields.Boolean(
        compute="_compute_is_sale_multiple_of_qty_set",
        recursive=True,
    )
    sale_own_multiple_of_qty = fields.Float(
        digits="Product Unit of Measure",
    )
    sale_inherited_multiple_of_qty = fields.Float(
        compute="_compute_sale_inherited_multiple_of_qty",
        digits="Product Unit of Measure",
        store=True,
        recursive=True,
    )
    sale_multiple_of_qty = fields.Float(
        help="The multiple-of quantity of product that can be sold.",
        compute="_compute_sale_multiple_of_qty",
        inverse="_inverse_sale_multiple_of_qty",
        store=True,
        recursive=True,
        digits="Product Unit of Measure",
    )

    is_sale_own_restrict_multiple_of_qty_set = fields.Boolean(
        compute="_compute_is_sale_own_restrict_multiple_of_qty_set",
        inverse="_inverse_is_sale_own_restrict_multiple_of_qty_set",
    )
    is_sale_inherited_restrict_multiple_of_qty_set = fields.Boolean(
        compute="_compute_is_sale_inherited_restrict_multiple_of_qty_set",
        recursive=True,
    )
    is_sale_restrict_multiple_of_qty_set = fields.Boolean(
        compute="_compute_is_sale_restrict_multiple_of_qty_set",
        recursive=True,
    )
    sale_own_restrict_multiple_of_qty = fields.Selection(
        selection=RESTRICTION_SELECTION,
    )
    sale_inherited_restrict_multiple_of_qty = fields.Selection(
        selection=RESTRICTION_SELECTION,
        compute="_compute_sale_inherited_restrict_multiple_of_qty",
        store=True,
        recursive=True,
    )
    sale_restrict_multiple_of_qty = fields.Selection(
        help="Enforce the multiple-of quantity of product that can be sold.",
        selection=RESTRICTION_SELECTION,
        compute="_compute_sale_restrict_multiple_of_qty",
        inverse="_inverse_sale_restrict_multiple_of_qty",
        store=True,
        recursive=True,
    )

    @api.onchange("is_sale_own_min_qty_set")
    def _onchange_is_sale_min_qty_set(self):
        if self.is_sale_own_min_qty_set:
            self.sale_own_min_qty = self.sale_inherited_min_qty
        else:
            self.sale_own_min_qty = 0.0

    def _get_is_sale_inherited_min_qty_set(self):
        self.ensure_one()
        return False

    def _compute_is_sale_inherited_min_qty_set(self):
        for rec in self:
            rec.is_sale_inherited_min_qty_set = rec._get_is_sale_inherited_min_qty_set()

    @api.depends("is_sale_own_min_qty_set", "is_sale_inherited_min_qty_set")
    def _compute_is_sale_min_qty_set(self):
        for rec in self:
            rec.is_sale_min_qty_set = (
                rec.is_sale_own_min_qty_set or rec.is_sale_inherited_min_qty_set
            )

    def _get_sale_inherited_min_qty(self):
        self.ensure_one()
        return 0.0

    def _compute_sale_inherited_min_qty(self):
        for rec in self:
            rec.sale_inherited_min_qty = rec._get_sale_inherited_min_qty()

    @api.depends(
        "is_sale_own_min_qty_set", "sale_own_min_qty", "sale_inherited_min_qty"
    )
    def _compute_sale_min_qty(self):
        for rec in self:
            if rec.is_sale_own_min_qty_set:
                rec.sale_min_qty = rec.sale_own_min_qty
            else:
                rec.sale_min_qty = rec.sale_inherited_min_qty

    def _inverse_sale_min_qty(self):
        for rec in self:
            if rec.sale_min_qty and rec.sale_min_qty != rec.sale_inherited_min_qty:
                rec.sale_own_min_qty = rec.sale_min_qty
                rec.is_sale_own_min_qty_set = True
            else:
                rec.sale_own_min_qty = 0.0
                rec.is_sale_own_min_qty_set = False

    @api.onchange("is_sale_own_restrict_min_qty_set")
    def _onchange_is_sale_restrict_min_qty_set(self):
        if self.is_sale_own_restrict_min_qty_set:
            self.sale_own_restrict_min_qty = self.sale_inherited_restrict_min_qty
        else:
            self.sale_own_restrict_min_qty = False

    def _compute_is_sale_own_restrict_min_qty_set(self):
        for rec in self:
            rec.is_sale_own_restrict_min_qty_set = bool(rec.sale_own_restrict_min_qty)

    def _inverse_is_sale_own_restrict_min_qty_set(self):
        if self.env.context.get("skip_sale_own_restrict_min_qty"):
            return
        for rec in self:
            if rec.is_sale_own_restrict_min_qty_set:
                rec.sale_own_restrict_min_qty = rec.sale_inherited_restrict_min_qty
            else:
                rec.sale_own_restrict_min_qty = None

    def _get_is_sale_inherited_restrict_min_qty_set(self):
        self.ensure_one()
        return False

    def _compute_is_sale_inherited_restrict_min_qty_set(self):
        for rec in self:
            rec.is_sale_inherited_restrict_min_qty_set = (
                rec._get_is_sale_inherited_restrict_min_qty_set()
            )

    @api.depends(
        "sale_own_restrict_min_qty",
        "sale_inherited_restrict_min_qty",
    )
    def _compute_is_sale_restrict_min_qty_set(self):
        for rec in self:
            rec.is_sale_restrict_min_qty_set = (
                rec.is_sale_own_restrict_min_qty_set
                or rec.is_sale_inherited_restrict_min_qty_set
            )

    def _get_sale_inherited_restrict_min_qty(self):
        self.ensure_one()
        return RESTRICTION_DISABLED

    def _compute_sale_inherited_restrict_min_qty(self):
        for rec in self:
            rec.sale_inherited_restrict_min_qty = (
                rec._get_sale_inherited_restrict_min_qty()
            )

    @api.depends(
        "sale_own_restrict_min_qty",
        "sale_inherited_restrict_min_qty",
    )
    def _compute_sale_restrict_min_qty(self):
        for rec in self:
            rec.sale_restrict_min_qty = (
                rec.sale_own_restrict_min_qty or rec.sale_inherited_restrict_min_qty
            )

    def _inverse_sale_restrict_min_qty(self):
        for rec in self.with_context(sale_own_restrict_min_qty=True):
            rec.is_sale_own_restrict_min_qty_set = True
            rec.sale_own_restrict_min_qty = rec.sale_restrict_min_qty

    @api.onchange("is_sale_own_max_qty_set")
    def _onchange_is_sale_max_qty_set(self):
        if self.is_sale_own_max_qty_set:
            self.sale_own_max_qty = self.sale_inherited_max_qty
        else:
            self.sale_own_max_qty = 0.0

    def _get_is_sale_inherited_max_qty_set(self):
        self.ensure_one()
        return False

    def _compute_is_sale_inherited_max_qty_set(self):
        for rec in self:
            rec.is_sale_inherited_max_qty_set = rec._get_is_sale_inherited_max_qty_set()

    @api.depends("is_sale_own_max_qty_set", "is_sale_inherited_max_qty_set")
    def _compute_is_sale_max_qty_set(self):
        for rec in self:
            rec.is_sale_max_qty_set = (
                rec.is_sale_own_max_qty_set or rec.is_sale_inherited_max_qty_set
            )

    def _get_sale_inherited_max_qty(self):
        self.ensure_one()
        return 0.0

    def _compute_sale_inherited_max_qty(self):
        for rec in self:
            rec.sale_inherited_max_qty = rec._get_sale_inherited_max_qty()

    @api.depends(
        "is_sale_own_max_qty_set", "sale_own_max_qty", "sale_inherited_max_qty"
    )
    def _compute_sale_max_qty(self):
        for rec in self:
            if rec.is_sale_own_max_qty_set:
                rec.sale_max_qty = rec.sale_own_max_qty
            else:
                rec.sale_max_qty = rec.sale_inherited_max_qty

    def _inverse_sale_max_qty(self):
        for rec in self:
            if rec.sale_max_qty and rec.sale_max_qty != rec.sale_inherited_max_qty:
                rec.sale_own_max_qty = rec.sale_max_qty
                rec.is_sale_own_max_qty_set = True
            else:
                rec.sale_own_max_qty = False
                rec.is_sale_own_max_qty_set = False

    @api.onchange("is_sale_own_restrict_max_qty_set")
    def _onchange_is_sale_restrict_max_qty_set(self):
        if self.is_sale_own_restrict_max_qty_set:
            self.sale_own_restrict_max_qty = self.sale_inherited_restrict_max_qty
        else:
            self.sale_own_restrict_max_qty = False

    def _compute_is_sale_own_restrict_max_qty_set(self):
        for rec in self:
            rec.is_sale_own_restrict_max_qty_set = bool(rec.sale_own_restrict_max_qty)

    def _inverse_is_sale_own_restrict_max_qty_set(self):
        if self.env.context.get("skip_sale_own_restrict_max_qty"):
            return
        for rec in self:
            if rec.is_sale_own_restrict_max_qty_set:
                rec.sale_own_restrict_max_qty = rec.sale_inherited_restrict_max_qty
            else:
                rec.sale_own_restrict_max_qty = None

    def _get_is_sale_inherited_restrict_max_qty_set(self):
        self.ensure_one()
        return False

    def _compute_is_sale_inherited_restrict_max_qty_set(self):
        for rec in self:
            rec.is_sale_inherited_restrict_max_qty_set = (
                rec._get_is_sale_inherited_restrict_max_qty_set()
            )

    @api.depends(
        "sale_own_restrict_max_qty",
        "sale_inherited_restrict_max_qty",
    )
    def _compute_is_sale_restrict_max_qty_set(self):
        for rec in self:
            rec.is_sale_restrict_max_qty_set = (
                rec.is_sale_own_restrict_max_qty_set
                or rec.is_sale_inherited_restrict_max_qty_set
            )

    def _get_sale_inherited_restrict_max_qty(self):
        self.ensure_one()
        return RESTRICTION_DISABLED

    def _compute_sale_inherited_restrict_max_qty(self):
        for rec in self:
            rec.sale_inherited_restrict_max_qty = (
                rec._get_sale_inherited_restrict_max_qty()
            )

    @api.depends(
        "sale_own_restrict_max_qty",
        "sale_inherited_restrict_max_qty",
    )
    def _compute_sale_restrict_max_qty(self):
        for rec in self:
            rec.sale_restrict_max_qty = (
                rec.sale_own_restrict_max_qty or rec.sale_inherited_restrict_max_qty
            )

    def _inverse_sale_restrict_max_qty(self):
        for rec in self.with_context(skip_sale_own_restrict_max_qty=True):
            rec.is_sale_own_restrict_max_qty_set = True
            rec.sale_own_restrict_max_qty = rec.sale_restrict_max_qty

    @api.onchange("is_sale_own_multiple_of_qty_set")
    def _onchange_is_sale_multiple_of_qty_set(self):
        if self.is_sale_own_multiple_of_qty_set:
            self.sale_own_multiple_of_qty = self.sale_inherited_multiple_of_qty
        else:
            self.sale_own_multiple_of_qty = 0.0

    def _get_is_sale_inherited_multiple_of_qty_set(self):
        self.ensure_one()
        return False

    def _compute_is_sale_inherited_multiple_of_qty_set(self):
        for rec in self:
            rec.is_sale_inherited_multiple_of_qty_set = (
                rec._get_is_sale_inherited_multiple_of_qty_set()
            )

    @api.depends(
        "is_sale_own_multiple_of_qty_set", "is_sale_inherited_multiple_of_qty_set"
    )
    def _compute_is_sale_multiple_of_qty_set(self):
        for rec in self:
            rec.is_sale_multiple_of_qty_set = (
                rec.is_sale_own_multiple_of_qty_set
                or rec.is_sale_inherited_multiple_of_qty_set
            )

    def _get_sale_inherited_multiple_of_qty(self):
        self.ensure_one()
        return 0.0

    def _compute_sale_inherited_multiple_of_qty(self):
        for rec in self:
            rec.sale_inherited_multiple_of_qty = (
                rec._get_sale_inherited_multiple_of_qty()
            )

    @api.depends(
        "is_sale_own_multiple_of_qty_set",
        "sale_own_multiple_of_qty",
        "sale_inherited_multiple_of_qty",
    )
    def _compute_sale_multiple_of_qty(self):
        for rec in self:
            if rec.is_sale_own_multiple_of_qty_set:
                rec.sale_multiple_of_qty = rec.sale_own_multiple_of_qty
            else:
                rec.sale_multiple_of_qty = rec.sale_inherited_multiple_of_qty

    def _inverse_sale_multiple_of_qty(self):
        for rec in self:
            if (
                rec.sale_multiple_of_qty
                and rec.sale_multiple_of_qty != rec.sale_inherited_multiple_of_qty
            ):
                rec.sale_own_multiple_of_qty = rec.sale_multiple_of_qty
                rec.is_sale_own_multiple_of_qty_set = True
            else:
                rec.sale_own_multiple_of_qty = False
                rec.is_sale_own_multiple_of_qty_set = False

    @api.onchange("is_sale_own_restrict_multiple_of_qty_set")
    def _onchange_is_sale_restrict_multiple_of_qty_set(self):
        if self.is_sale_own_restrict_multiple_of_qty_set:
            self.sale_own_restrict_multiple_of_qty = (
                self.sale_inherited_restrict_multiple_of_qty
            )
        else:
            self.sale_own_restrict_multiple_of_qty = None

    def _compute_is_sale_own_restrict_multiple_of_qty_set(self):
        for rec in self:
            rec.is_sale_own_restrict_multiple_of_qty_set = bool(
                rec.sale_own_restrict_multiple_of_qty
            )

    def _inverse_is_sale_own_restrict_multiple_of_qty_set(self):
        if self.env.context.get("skip_sale_own_restrict_multiple_of_qty"):
            return
        for rec in self:
            if rec.is_sale_own_restrict_multiple_of_qty_set:
                rec.sale_own_restrict_multiple_of_qty = (
                    rec.sale_inherited_restrict_multiple_of_qty
                )
            else:
                rec.sale_own_restrict_multiple_of_qty = None

    def _get_is_sale_inherited_restrict_multiple_of_qty_set(self):
        self.ensure_one()
        return False

    def _compute_is_sale_inherited_restrict_multiple_of_qty_set(self):
        for rec in self:
            rec.is_sale_inherited_restrict_multiple_of_qty_set = (
                rec._get_is_sale_inherited_restrict_multiple_of_qty_set()
            )

    @api.depends(
        "sale_own_restrict_multiple_of_qty",
        "sale_inherited_restrict_multiple_of_qty",
    )
    def _compute_is_sale_restrict_multiple_of_qty_set(self):
        for rec in self:
            rec.is_sale_restrict_multiple_of_qty_set = (
                rec.is_sale_own_restrict_multiple_of_qty_set
                or rec.is_sale_inherited_restrict_multiple_of_qty_set
            )

    def _get_sale_inherited_restrict_multiple_of_qty(self):
        self.ensure_one()
        return RESTRICTION_DISABLED

    def _compute_sale_inherited_restrict_multiple_of_qty(self):
        for rec in self:
            rec.sale_inherited_restrict_multiple_of_qty = (
                rec._get_sale_inherited_restrict_multiple_of_qty()
            )

    @api.depends(
        "sale_own_restrict_multiple_of_qty",
        "sale_inherited_restrict_multiple_of_qty",
    )
    def _compute_sale_restrict_multiple_of_qty(self):
        for rec in self:
            rec.sale_restrict_multiple_of_qty = (
                rec.sale_own_restrict_multiple_of_qty
                or rec.sale_inherited_restrict_multiple_of_qty
            )

    def _inverse_sale_restrict_multiple_of_qty(self):
        for rec in self.with_context(skip_sale_own_restrict_multiple_of_qty=True):
            rec.is_sale_own_restrict_multiple_of_qty_set = True
            rec.sale_own_restrict_multiple_of_qty = rec.sale_restrict_multiple_of_qty
