# Copyright 2026 Openred
# © 2010-2012 Andy Lu <andy.lu@elico-corp.com> (Elico Corp)
# © 2013 Agile Business Group sagl (<http://www.agilebg.com>)
# © 2017 valentin vinagre  <valentin.vinagre@qubiq.es> (QubiQ)
# © 2020 Manuel Regidor  <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import _, api, models

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _is_placeholder_order_name(self, name):
        # openred: v19 usa _('New') como nombre provisional antes de asignar secuencia
        return not name or name == _("New")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if self._is_placeholder_order_name(vals.get("name")):
                if self.is_using_quotation_number(vals):
                    company_id = vals.get("company_id", self.env.company.id)
                    sequence = (
                        self.with_company(company_id)
                        .env["ir.sequence"]
                        .next_by_code("sale.quotation")
                    )
                    vals["name"] = sequence or "/"
                    # openred: log pruebas
                    _logger.info("Presupuesto creado: %s", vals["name"])
        return super().create(vals_list)

    @api.model
    def is_using_quotation_number(self, vals):
        company = False
        if vals.get("company_id"):
            company = self.env["res.company"].browse(vals.get("company_id"))
        else:
            company = self.env.company
        return not company.keep_name_so

    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        if self.origin and self.origin != "":
            default["origin"] = self.origin + ", " + self.name
        else:
            default["origin"] = self.name
        # openred: log pruebas
        _logger.info("Presupuesto duplicado, origen: %s", default["origin"])
        return super().copy(default)

    def action_confirm(self):
        quotation_sequence = self.env["ir.sequence"].search(
            [("code", "=", "sale.quotation")], limit=1
        )
        for order in self:
            if (
                quotation_sequence
                and order.name[: len(quotation_sequence.prefix)]
                != quotation_sequence.prefix
            ):
                continue
            if order.state not in ("draft", "sent") or order.company_id.keep_name_so:
                continue
            quotation_name = order.name
            if order.origin and order.origin != "":
                quo = order.origin + ", " + order.name
            else:
                quo = order.name
            order_sequence = (
                self.with_company(order.company_id.id)
                .env["ir.sequence"]
                .next_by_code("sale.order")
            )
            # openred: log pruebas
            _logger.info(
                "Presupuesto confirmado: %s -> %s", quotation_name, order_sequence
            )
            order.write({"origin": quo, "name": order_sequence})
        return super().action_confirm()
