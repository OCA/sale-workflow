# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from lxml import etree

from odoo import _, api, exceptions, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    user_can_confirm = fields.Boolean(
        compute="_compute_user_can_confirm", compute_sudo=False
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
        for sale in self:
            company = sale.company_id.sudo()
            if not company.use_sale_confirmation_groups:
                sale.user_can_confirm = True
            elif not (groups := company.sale_confirmation_group_ids):
                sale.user_can_confirm = True
            else:
                sale.user_can_confirm = (
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
            _(
                "User %(user)s cannot confirm Sale(s) %(sales)s",
                user=self.env.user.name,
                sales=", ".join(
                    f"'{sale.display_name}'" for sale in self - can_confirm
                ),
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
        arch, view = super()._get_view(view_id=view_id, view_type=view_type, **options)
        buttons = arch.xpath("//button[@name='action_confirm']")
        if buttons and not arch.xpath("./field[@name='user_can_confirm']"):
            # Odoo 17 does not automatically add fields used by modifiers.
            etree.SubElement(arch, "field", name="user_can_confirm", invisible="1")
        for node in buttons:
            if value := node.get("invisible"):
                node.set("invisible", f"not user_can_confirm or ({value})")
            else:
                node.set("invisible", "not user_can_confirm")
        return arch, view
