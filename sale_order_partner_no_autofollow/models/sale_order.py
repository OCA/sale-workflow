from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def message_subscribe(self, partner_ids=None, subtype_ids=None):
        partner_ids = partner_ids or []
        if (
            self._context.get("sale_partner_disable_autofollow")
            and self.partner_id.id in partner_ids
        ):
            partner_ids.remove(self.partner_id.id)
        return super(SaleOrder, self).message_subscribe(partner_ids, subtype_ids)

    @api.model_create_multi
    def create(self, values):
        return super(
            SaleOrder,
            self.with_context(
                sale_partner_disable_autofollow=self._partner_disable_autofollow()
            ),
        ).create(values)

    def action_confirm(self):
        return super(
            SaleOrder,
            self.with_context(
                sale_partner_disable_autofollow=self._partner_disable_autofollow()
            ),
        ).action_confirm()

    def _partner_disable_autofollow(self):
        """Returns the state of the "Customer disable autofollow" option

        Returns:
            bool: Option status
        """
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "sale_order_partner_no_autofollow.partner_disable_autofollow", False
            )
        )
