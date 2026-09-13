# Copyright 2019 Akretion
# Copyright 2024 CorporateHub
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

RESTRICTION_ENABLED = "blocking"
RESTRICTION_DISABLED = "warning"
RESTRICTION_SELECTION = [
    (RESTRICTION_ENABLED, "Blocking"),
    (RESTRICTION_DISABLED, "Warning"),
]


class ProductRestrictedQtyMixin(models.AbstractModel):
    _name = "sale.product.restricted.qty.mixin"
    _description = "Product Restricted Qty Mixin"

    _sale_restricted_qty_parent_field = None

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

    is_sale_own_restrict_min_qty_set = fields.Boolean()
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
        help="Decide if the minimum quantity constraint is strictly enforced "
        "(Blocking) or if it only triggers a warning (Warning).\n"
        "Use 'Warning' if you want to allow exceptions like selling samples "
        "or leftover stock.",
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

    is_sale_own_restrict_max_qty_set = fields.Boolean()
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
        help="Decide if the maximum quantity constraint is strictly enforced "
        "(Blocking) or if it only triggers a warning (Warning).\n"
        "Use 'Warning' if you want to allow large orders that exceed strict "
        "policies under special conditions.",
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

    is_sale_own_restrict_multiple_of_qty_set = fields.Boolean()
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
        help="Decide if the multiple-of quantity constraint is strictly enforced "
        "(Blocking) or if it only triggers a warning (Warning).\n"
        "Use 'Warning' to allow selling non-standard quantities for special "
        "cases like clearing leftover stock.",
        selection=RESTRICTION_SELECTION,
        compute="_compute_sale_restrict_multiple_of_qty",
        inverse="_inverse_sale_restrict_multiple_of_qty",
        store=True,
        recursive=True,
    )

    # --- min_qty ---

    @api.onchange("is_sale_own_min_qty_set")
    def _onchange_is_sale_min_qty_set(self):
        if self.is_sale_own_min_qty_set:
            self.sale_own_min_qty = self.sale_inherited_min_qty
        else:
            self.sale_own_min_qty = 0.0
        # A restriction mode is meaningless without a quantity value.
        if not self.is_sale_min_qty_set:
            self.is_sale_own_restrict_min_qty_set = False
            self.sale_own_restrict_min_qty = False

    def _get_is_sale_inherited_min_qty_set(self):
        self.ensure_one()
        parent_field = self._sale_restricted_qty_parent_field
        if not parent_field or not self[parent_field]:
            return False
        return self[parent_field].is_sale_min_qty_set

    @api.depends(
        lambda self: (
            [f"{self._sale_restricted_qty_parent_field}.is_sale_min_qty_set"]
            if self._sale_restricted_qty_parent_field
            else []
        )
    )
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
        parent_field = self._sale_restricted_qty_parent_field
        if not parent_field or not self[parent_field]:
            return 0.0
        return self[parent_field].sale_min_qty

    @api.depends(
        lambda self: (
            [f"{self._sale_restricted_qty_parent_field}.sale_min_qty"]
            if self._sale_restricted_qty_parent_field
            else []
        )
    )
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

    # --- restrict_min_qty ---

    @api.onchange("is_sale_own_restrict_min_qty_set")
    def _onchange_is_sale_restrict_min_qty_set(self):
        if self.is_sale_own_restrict_min_qty_set:
            self.sale_own_restrict_min_qty = self.sale_inherited_restrict_min_qty
        else:
            self.sale_own_restrict_min_qty = False

    def _get_is_sale_inherited_restrict_min_qty_set(self):
        self.ensure_one()
        parent_field = self._sale_restricted_qty_parent_field
        if not parent_field or not self[parent_field]:
            return False
        return self[parent_field].is_sale_restrict_min_qty_set

    @api.depends(
        lambda self: (
            [
                f"{self._sale_restricted_qty_parent_field}"
                f".is_sale_restrict_min_qty_set"
            ]
            if self._sale_restricted_qty_parent_field
            else []
        )
    )
    def _compute_is_sale_inherited_restrict_min_qty_set(self):
        for rec in self:
            rec.is_sale_inherited_restrict_min_qty_set = (
                rec._get_is_sale_inherited_restrict_min_qty_set()
            )

    @api.depends(
        "is_sale_own_restrict_min_qty_set",
        "is_sale_inherited_restrict_min_qty_set",
    )
    def _compute_is_sale_restrict_min_qty_set(self):
        for rec in self:
            rec.is_sale_restrict_min_qty_set = (
                rec.is_sale_own_restrict_min_qty_set
                or rec.is_sale_inherited_restrict_min_qty_set
            )

    def _get_sale_inherited_restrict_min_qty(self):
        self.ensure_one()
        parent_field = self._sale_restricted_qty_parent_field
        if not parent_field or not self[parent_field]:
            return RESTRICTION_DISABLED
        return self[parent_field].sale_restrict_min_qty

    @api.depends(
        lambda self: (
            [f"{self._sale_restricted_qty_parent_field}.sale_restrict_min_qty"]
            if self._sale_restricted_qty_parent_field
            else []
        )
    )
    def _compute_sale_inherited_restrict_min_qty(self):
        for rec in self:
            rec.sale_inherited_restrict_min_qty = (
                rec._get_sale_inherited_restrict_min_qty()
            )

    @api.depends(
        "is_sale_own_restrict_min_qty_set",
        "sale_own_restrict_min_qty",
        "sale_inherited_restrict_min_qty",
    )
    def _compute_sale_restrict_min_qty(self):
        for rec in self:
            if rec.is_sale_own_restrict_min_qty_set:
                rec.sale_restrict_min_qty = rec.sale_own_restrict_min_qty
            else:
                rec.sale_restrict_min_qty = rec.sale_inherited_restrict_min_qty

    def _inverse_sale_restrict_min_qty(self):
        for rec in self:
            if (
                rec.sale_restrict_min_qty
                and rec.sale_restrict_min_qty != rec.sale_inherited_restrict_min_qty
            ):
                rec.sale_own_restrict_min_qty = rec.sale_restrict_min_qty
                rec.is_sale_own_restrict_min_qty_set = True
            else:
                rec.sale_own_restrict_min_qty = False
                rec.is_sale_own_restrict_min_qty_set = False

    # --- max_qty ---

    @api.onchange("is_sale_own_max_qty_set")
    def _onchange_is_sale_max_qty_set(self):
        if self.is_sale_own_max_qty_set:
            self.sale_own_max_qty = self.sale_inherited_max_qty
        else:
            self.sale_own_max_qty = 0.0
        # A restriction mode is meaningless without a quantity value.
        if not self.is_sale_max_qty_set:
            self.is_sale_own_restrict_max_qty_set = False
            self.sale_own_restrict_max_qty = False

    def _get_is_sale_inherited_max_qty_set(self):
        self.ensure_one()
        parent_field = self._sale_restricted_qty_parent_field
        if not parent_field or not self[parent_field]:
            return False
        return self[parent_field].is_sale_max_qty_set

    @api.depends(
        lambda self: (
            [f"{self._sale_restricted_qty_parent_field}.is_sale_max_qty_set"]
            if self._sale_restricted_qty_parent_field
            else []
        )
    )
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
        parent_field = self._sale_restricted_qty_parent_field
        if not parent_field or not self[parent_field]:
            return 0.0
        return self[parent_field].sale_max_qty

    @api.depends(
        lambda self: (
            [f"{self._sale_restricted_qty_parent_field}.sale_max_qty"]
            if self._sale_restricted_qty_parent_field
            else []
        )
    )
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
                rec.sale_own_max_qty = 0.0
                rec.is_sale_own_max_qty_set = False

    # --- restrict_max_qty ---

    @api.onchange("is_sale_own_restrict_max_qty_set")
    def _onchange_is_sale_restrict_max_qty_set(self):
        if self.is_sale_own_restrict_max_qty_set:
            self.sale_own_restrict_max_qty = self.sale_inherited_restrict_max_qty
        else:
            self.sale_own_restrict_max_qty = False

    def _get_is_sale_inherited_restrict_max_qty_set(self):
        self.ensure_one()
        parent_field = self._sale_restricted_qty_parent_field
        if not parent_field or not self[parent_field]:
            return False
        return self[parent_field].is_sale_restrict_max_qty_set

    @api.depends(
        lambda self: (
            [
                f"{self._sale_restricted_qty_parent_field}"
                f".is_sale_restrict_max_qty_set"
            ]
            if self._sale_restricted_qty_parent_field
            else []
        )
    )
    def _compute_is_sale_inherited_restrict_max_qty_set(self):
        for rec in self:
            rec.is_sale_inherited_restrict_max_qty_set = (
                rec._get_is_sale_inherited_restrict_max_qty_set()
            )

    @api.depends(
        "is_sale_own_restrict_max_qty_set",
        "is_sale_inherited_restrict_max_qty_set",
    )
    def _compute_is_sale_restrict_max_qty_set(self):
        for rec in self:
            rec.is_sale_restrict_max_qty_set = (
                rec.is_sale_own_restrict_max_qty_set
                or rec.is_sale_inherited_restrict_max_qty_set
            )

    def _get_sale_inherited_restrict_max_qty(self):
        self.ensure_one()
        parent_field = self._sale_restricted_qty_parent_field
        if not parent_field or not self[parent_field]:
            return RESTRICTION_DISABLED
        return self[parent_field].sale_restrict_max_qty

    @api.depends(
        lambda self: (
            [f"{self._sale_restricted_qty_parent_field}.sale_restrict_max_qty"]
            if self._sale_restricted_qty_parent_field
            else []
        )
    )
    def _compute_sale_inherited_restrict_max_qty(self):
        for rec in self:
            rec.sale_inherited_restrict_max_qty = (
                rec._get_sale_inherited_restrict_max_qty()
            )

    @api.depends(
        "is_sale_own_restrict_max_qty_set",
        "sale_own_restrict_max_qty",
        "sale_inherited_restrict_max_qty",
    )
    def _compute_sale_restrict_max_qty(self):
        for rec in self:
            if rec.is_sale_own_restrict_max_qty_set:
                rec.sale_restrict_max_qty = rec.sale_own_restrict_max_qty
            else:
                rec.sale_restrict_max_qty = rec.sale_inherited_restrict_max_qty

    def _inverse_sale_restrict_max_qty(self):
        for rec in self:
            if (
                rec.sale_restrict_max_qty
                and rec.sale_restrict_max_qty != rec.sale_inherited_restrict_max_qty
            ):
                rec.sale_own_restrict_max_qty = rec.sale_restrict_max_qty
                rec.is_sale_own_restrict_max_qty_set = True
            else:
                rec.sale_own_restrict_max_qty = False
                rec.is_sale_own_restrict_max_qty_set = False

    # --- multiple_of_qty ---

    @api.onchange("is_sale_own_multiple_of_qty_set")
    def _onchange_is_sale_multiple_of_qty_set(self):
        if self.is_sale_own_multiple_of_qty_set:
            self.sale_own_multiple_of_qty = self.sale_inherited_multiple_of_qty
        else:
            self.sale_own_multiple_of_qty = 0.0
        # A restriction mode is meaningless without a quantity value.
        if not self.is_sale_multiple_of_qty_set:
            self.is_sale_own_restrict_multiple_of_qty_set = False
            self.sale_own_restrict_multiple_of_qty = False

    def _get_is_sale_inherited_multiple_of_qty_set(self):
        self.ensure_one()
        parent_field = self._sale_restricted_qty_parent_field
        if not parent_field or not self[parent_field]:
            return False
        return self[parent_field].is_sale_multiple_of_qty_set

    @api.depends(
        lambda self: (
            [
                f"{self._sale_restricted_qty_parent_field}"
                f".is_sale_multiple_of_qty_set"
            ]
            if self._sale_restricted_qty_parent_field
            else []
        )
    )
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
        parent_field = self._sale_restricted_qty_parent_field
        if not parent_field or not self[parent_field]:
            return 0.0
        return self[parent_field].sale_multiple_of_qty

    @api.depends(
        lambda self: (
            [f"{self._sale_restricted_qty_parent_field}.sale_multiple_of_qty"]
            if self._sale_restricted_qty_parent_field
            else []
        )
    )
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
                rec.sale_own_multiple_of_qty = 0.0
                rec.is_sale_own_multiple_of_qty_set = False

    # --- restrict_multiple_of_qty ---

    @api.onchange("is_sale_own_restrict_multiple_of_qty_set")
    def _onchange_is_sale_restrict_multiple_of_qty_set(self):
        if self.is_sale_own_restrict_multiple_of_qty_set:
            self.sale_own_restrict_multiple_of_qty = (
                self.sale_inherited_restrict_multiple_of_qty
            )
        else:
            self.sale_own_restrict_multiple_of_qty = None

    def _get_is_sale_inherited_restrict_multiple_of_qty_set(self):
        self.ensure_one()
        parent_field = self._sale_restricted_qty_parent_field
        if not parent_field or not self[parent_field]:
            return False
        return self[parent_field].is_sale_restrict_multiple_of_qty_set

    @api.depends(
        lambda self: (
            [
                f"{self._sale_restricted_qty_parent_field}"
                f".is_sale_restrict_multiple_of_qty_set"
            ]
            if self._sale_restricted_qty_parent_field
            else []
        )
    )
    def _compute_is_sale_inherited_restrict_multiple_of_qty_set(self):
        for rec in self:
            rec.is_sale_inherited_restrict_multiple_of_qty_set = (
                rec._get_is_sale_inherited_restrict_multiple_of_qty_set()
            )

    @api.depends(
        "is_sale_own_restrict_multiple_of_qty_set",
        "is_sale_inherited_restrict_multiple_of_qty_set",
    )
    def _compute_is_sale_restrict_multiple_of_qty_set(self):
        for rec in self:
            rec.is_sale_restrict_multiple_of_qty_set = (
                rec.is_sale_own_restrict_multiple_of_qty_set
                or rec.is_sale_inherited_restrict_multiple_of_qty_set
            )

    def _get_sale_inherited_restrict_multiple_of_qty(self):
        self.ensure_one()
        parent_field = self._sale_restricted_qty_parent_field
        if not parent_field or not self[parent_field]:
            return RESTRICTION_DISABLED
        return self[parent_field].sale_restrict_multiple_of_qty

    @api.depends(
        lambda self: (
            [
                f"{self._sale_restricted_qty_parent_field}"
                f".sale_restrict_multiple_of_qty"
            ]
            if self._sale_restricted_qty_parent_field
            else []
        )
    )
    def _compute_sale_inherited_restrict_multiple_of_qty(self):
        for rec in self:
            rec.sale_inherited_restrict_multiple_of_qty = (
                rec._get_sale_inherited_restrict_multiple_of_qty()
            )

    @api.depends(
        "is_sale_own_restrict_multiple_of_qty_set",
        "sale_own_restrict_multiple_of_qty",
        "sale_inherited_restrict_multiple_of_qty",
    )
    def _compute_sale_restrict_multiple_of_qty(self):
        for rec in self:
            if rec.is_sale_own_restrict_multiple_of_qty_set:
                rec.sale_restrict_multiple_of_qty = (
                    rec.sale_own_restrict_multiple_of_qty
                )
            else:
                rec.sale_restrict_multiple_of_qty = (
                    rec.sale_inherited_restrict_multiple_of_qty
                )

    def _inverse_sale_restrict_multiple_of_qty(self):
        for rec in self:
            if (
                rec.sale_restrict_multiple_of_qty
                and rec.sale_restrict_multiple_of_qty
                != rec.sale_inherited_restrict_multiple_of_qty
            ):
                rec.sale_own_restrict_multiple_of_qty = (
                    rec.sale_restrict_multiple_of_qty
                )
                rec.is_sale_own_restrict_multiple_of_qty_set = True
            else:
                rec.sale_own_restrict_multiple_of_qty = False
                rec.is_sale_own_restrict_multiple_of_qty_set = False

    # --- data repair (called from migrations/18.0.3.0.0) ---

    @api.model
    def _repair_restrict_inheritance(self):
        """Normalise stored restriction modes after the own-set flags became
        independent stored booleans.

        - ``product.category`` / ``product.template``: keep a genuine override
          (own mode set, differing from the inherited mode, with a quantity
          value to act on) and mark the new flag; drop redundant (own equal to
          inherited) or orphan (no value) modes so they re-inherit.
        - ``product.product`` (variant): drop every own restriction mode so
          variants always inherit their template. Variant-level restriction
          overrides were, in practice, artefacts of the previous always-pinning
          inverse; deliberate configuration lives on the template/category.
        """
        config_models = (
            ("product.category", "parent_path"),
            ("product.template", "id"),
        )
        for field in ("min", "max", "multiple_of"):
            own_field = f"sale_own_restrict_{field}_qty"
            inherited_field = f"sale_inherited_restrict_{field}_qty"
            flag_field = f"is_sale_own_restrict_{field}_qty_set"
            value_set_field = f"is_sale_{field}_qty_set"

            for model_name, order in config_models:
                for rec in self.env[model_name].search([], order=order):
                    own = rec[own_field]
                    if not own:
                        continue
                    if not rec[value_set_field] or own == rec[inherited_field]:
                        rec[own_field] = False
                        rec[flag_field] = False
                    else:
                        rec[flag_field] = True
                # Flush so children recompute their inherited value.
                self.env.invalidate_all()

            variants = self.env["product.product"].search([(own_field, "!=", False)])
            if variants:
                variants.write({own_field: False, flag_field: False})
                self.env.invalidate_all()
