# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, exceptions, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    user_can_confirm = fields.Boolean(
        compute="_compute_user_can_confirm", compute_sudo=True
    )

    @api.depends(
        # Keep these dotted fields as dependencies, because:
        # - chances of them being updated very often (leading to lots of records cache
        #   invalidations and field recomputation) are quite low
        # - removing them in favor of ``company_id`` alone (or no deps at all) means
        #   we'd have to invalidate the records cache manually when we need to check
        #   whether a user can actually confirm a sale order (to avoid using an outdated
        #   value for this field, since settings may have been updated in the meanwhile)
        "company_id.use_sale_confirmation_groups",
        "company_id.sale_confirmation_group_ids.users",
    )
    @api.depends_context("uid")
    def _compute_user_can_confirm(self):
        user = self.env.user
        for company, sales in self.grouped("company_id").items():
            if not company.use_sale_confirmation_groups:
                sales.user_can_confirm = True
            elif not (groups := company.sale_confirmation_group_ids):
                sales.user_can_confirm = True
            else:
                sales.user_can_confirm = (
                    user in groups.with_context(active_test=False).users
                )

    def action_confirm(self):
        # OVERRIDE: prevent unallowed users from confirming a sale order,
        # and raise a ``ValidationError`` instead

        # 1- check skipped: exit early
        if self._skip_check_user_can_confirm():
            return super().action_confirm()

        # 2- all SO in ``self`` can be confirmed
        elif (can_confirm := self._filter_user_can_confirm()) == self:
            return super().action_confirm()

        # 3- at least 1 SO cannot be confirmed by the user
        raise exceptions.ValidationError(
            self.env._(
                "User %s cannot confirm Sale(s) %s",
                self.env.user.name,
                ", ".join((self - can_confirm).mapped(lambda s: f"'{s.display_name}'")),
            )
        )

    def _skip_check_user_can_confirm(self) -> bool:
        """Defines whether checks upon user permissions to confirm should be skipped

        Set context key "skip_check_user_can_confirm" as ``True`` to skip the checks.
        """
        return bool(self.env.context.get("skip_check_user_can_confirm", self.env.su))

    def _filter_user_can_confirm(self) -> "SaleOrder":
        """Returns the subset of records that the current user can confirm

        Hook method, can be overridden
        """
        return self.filtered("user_can_confirm")

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        # OVERRIDE: hide the SO ``action_confirm`` button to users who shouldn't be
        # allowed confirmation
        # NB: we override ``sale.order._get_view()``, not ``sale.order.get_view()``,
        # because:
        # - the result of ``sale.order._get_view()`` is cached
        # - the result of ``sale.order._get_view()`` is updated by method
        #   ``ir.ui.view._add_missing_fields()`` to automatically add fields needed for
        #   the evaluation of nodes' attributes (required, invisible, etc...),
        #   so we don't need to do it here
        arch, view = super()._get_view(view_id=view_id, view_type=view_type, **options)
        for node in arch.xpath("//button[@name='action_confirm']"):
            if value := node.get("invisible"):
                node.set("invisible", f"not user_can_confirm or ({value})")
            else:
                node.set("invisible", "not user_can_confirm")
        return arch, view
