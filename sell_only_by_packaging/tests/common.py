# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.fields import Command
from odoo.tests import TransactionCase

TU_PRODUCT_QTY = 20
PL_PRODUCT_QTY = TU_PRODUCT_QTY * 30


class SellOnlyByPackagingCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.env.user.group_ids += cls.env.ref("uom.group_uom")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        # Packagings are plain units of measure since 19.0: a transport unit of
        # 20 products, and a pallet of 30 transport units.
        cls.uom_tu = cls.env["uom.uom"].create(
            {
                "name": "Test TU",
                "relative_factor": TU_PRODUCT_QTY,
                "relative_uom_id": cls.uom_unit.id,
            }
        )
        cls.uom_pl = cls.env["uom.uom"].create(
            {
                "name": "Test PL",
                "relative_factor": PL_PRODUCT_QTY / TU_PRODUCT_QTY,
                "relative_uom_id": cls.uom_tu.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product sold by packaging",
                "type": "consu",
                "sale_ok": True,
                "uom_id": cls.uom_unit.id,
                "uom_ids": [Command.set([cls.uom_tu.id, cls.uom_pl.id])],
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 0.0,
                        }
                    )
                ],
            }
        )
        cls.order_line = cls.order.order_line
