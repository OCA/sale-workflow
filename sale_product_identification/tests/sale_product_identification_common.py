# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestSaleOrderIdentificationCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ResPartnerIdCategory = cls.env["res.partner.id_category"]
        SaleOrder = cls.env["sale.order"]
        ProductTemplate = cls.env["product.template"]
        ResPartner = cls.env["res.partner"]
        cls.category_corrosive = ResPartnerIdCategory.create(
            {"code": "id_corrosive", "name": "Corrosive"}
        )
        cls.category_bilogical = ResPartnerIdCategory.create(
            {"code": "id_bilogical", "name": "Bilogical"}
        )
        cls.category_explosive = ResPartnerIdCategory.create(
            {"code": "id_explosive", "name": "Explosive"}
        )

        cls.partner_id = ResPartner.create(
            {
                "name": "Partner Test",
                "id_numbers": [
                    Command.create(
                        {
                            "name": "Bad ID",
                            "category_id": cls.category_corrosive.id,
                        }
                    )
                ],
            }
        )
        cls.product_tmpl_with_iden = ProductTemplate.create(
            {
                "name": "Product Test Iden",
                "required_identification": True,
                "product_tmpl_category_ids": [
                    Command.create(
                        {
                            "category_id": cls.category_corrosive.id,
                            "is_mandatory": True,
                        }
                    ),
                    Command.create(
                        {
                            "category_id": cls.category_bilogical.id,
                            "is_mandatory": True,
                        }
                    ),
                ],
            }
        )
        cls.product_with_iden = cls.product_tmpl_with_iden.product_variant_ids[:1]
        cls.product_tmpl_with_iden_opt = ProductTemplate.create(
            {
                "name": "Product Test optional",
                "required_identification": True,
                "product_tmpl_category_ids": [
                    Command.create(
                        {
                            "category_id": cls.category_corrosive.id,
                            "is_mandatory": False,
                        }
                    ),
                    Command.create(
                        {
                            "category_id": cls.category_bilogical.id,
                            "is_mandatory": True,
                        }
                    ),
                    Command.create(
                        {
                            "category_id": cls.category_explosive.id,
                            "is_mandatory": False,
                        }
                    ),
                ],
            }
        )
        cls.product_with_iden_opt = cls.product_tmpl_with_iden_opt.product_variant_ids[
            :1
        ]
        cls.product_tmpl_without_iden = ProductTemplate.create(
            {
                "name": "Product Test",
            }
        )
        cls.product_without_iden = cls.product_tmpl_without_iden.product_variant_ids[:1]

        cls.order = SaleOrder.create(
            {
                "name": "Sale Order Test",
                "partner_id": cls.partner_id.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.product_tmpl_with_iden.name,
                            "product_id": cls.product_with_iden.id,
                            "product_uom_qty": 5,
                        }
                    ),
                    Command.create(
                        {
                            "name": cls.product_tmpl_without_iden.name,
                            "product_id": cls.product_without_iden.id,
                            "product_uom_qty": 6,
                        }
                    ),
                ],
            }
        )
        cls.order_opt = SaleOrder.create(
            {
                "name": "Sale Order Test Optional",
                "partner_id": cls.partner_id.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.product_tmpl_with_iden_opt.name,
                            "product_id": cls.product_with_iden_opt.id,
                            "product_uom_qty": 5,
                        }
                    )
                ],
            }
        )
