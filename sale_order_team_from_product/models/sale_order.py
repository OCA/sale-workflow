# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import str2bool

from .res_config_settings import _PARAM_SET_FROM_PRODUCTS, _PARAM_SKIP_IF_SET


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _get_sales_team_from_product_config(self) -> tuple[bool, bool]:
        """Get configuration flags controlling Sales Team behavior.

        This helper reads the system parameters configured through
        the Settings form:

        - _PARAM_SET_FROM_PRODUCTS - whether the Sales Team should be
          automatically taken from products.
        - _PARAM_SKIP_IF_SET - whether to skip orders that already have
          a Sales Team set.

        :return: A tuple (enabled, skip_if_set), both being booleans.
        """
        ICP = self.env["ir.config_parameter"].sudo()
        enabled = str2bool(ICP.get_param(_PARAM_SET_FROM_PRODUCTS, "False"))
        skip_if_set = str2bool(ICP.get_param(_PARAM_SKIP_IF_SET, "False"))
        return enabled, skip_if_set

    def _get_sales_team_from_products(self):
        """Compute a single Sales Team from the products on this order.

        The logic is:
        - Collect sales_team_id from related product templates on all
          order lines.
        - Ignore empty values.
        - If exactly one unique team is found, return that team recordset.
        - If there are no teams or more than one distinct team, return False.

        :return: An integer team ID when exactly one unique team is found, or False.
        """
        self.ensure_one()
        team_ids = set(self.order_line.product_id.product_tmpl_id.sales_team_id.ids)
        if len(team_ids) == 1:
            return next(iter(team_ids))
        return False

    def _apply_sales_team_from_products(self, skip_if_set: bool) -> None:
        """Apply a Sales Team from products to draft/sent quotations.

        For each order in the recordset:
        - Only orders in states draft or sent are considered;
        - If skip_if_set is True and the order already has a
          team_id (either computed by the core logic or manually set),
          the order is left unchanged;
        - Otherwise :meth:_get_sales_team_from_products is called and,
          if it returns a single team, that team is directly assigned
          to team_id.

        :param skip_if_set: If True, do not override an already set
            Sales Team on the quotation.
        :return: None.
        """
        for order in self:
            # We do not touch confirmed orders
            if order.state not in ("draft", "sent"):
                continue
            if skip_if_set and order.team_id:
                continue
            team_id = order._get_sales_team_from_products()
            if not team_id:
                continue
            order.team_id = team_id

    @api.depends("order_line.product_id.product_tmpl_id.sales_team_id")
    def _compute_team_id(self) -> None:
        """Extend the default team computation with product-based logic.

        Base implementation computes the default Sales Team from the
        salesperson, partner and company.

        This override keeps the original behavior and,
        if the feature is enabled, optionally replaces the result with the
        team coming from the products on the order.
        """
        # pylint: disable=W8110
        # First, let the core logic compute the default team.
        super()._compute_team_id()

        # Then, optionally override it using product configuration.
        enabled, skip_if_set = self._get_sales_team_from_product_config()
        if enabled:
            self._apply_sales_team_from_products(skip_if_set)
