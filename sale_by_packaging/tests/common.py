# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import Form, SavepointCase

TU_PRODUCT_QTY = 20
PL_PRODUCT_QTY = TU_PRODUCT_QTY * 30


class Common(SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super(Common, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.setUpClassPartner()
        cls.setUpClassProduct()
        cls.setUpClassPackagingType()
        cls.setUpClassPackaging()
        cls.setUpClassSaleOrder()
        cls.setUpClassConfig()

    @classmethod
    def setUpClassConfig(cls):
        cls.precision = cls.env["decimal.precision"].precision_get("Product Price")

    @classmethod
    def setUpClassPartner(cls):
        cls.partner = cls.env.ref("base.res_partner_12")

    @classmethod
    def setUpClassProduct(cls):
        cls.product = cls.env.ref("product.product_product_9")

    @classmethod
    def setUpClassPackagingType(cls):
        cls.packaging_type_tu = cls.env["product.packaging.type"].create(
            {"name": "Transport Unit", "code": "TU", "sequence": 1}
        )
        cls.packaging_type_pl = cls.env["product.packaging.type"].create(
            {"name": "Pallet", "code": "PL", "sequence": 2}
        )
        cls.packaging_type_cannot_be_sold = cls.env["product.packaging.type"].create(
            {
                "name": "Can not be sold",
                "code": "CNBS",
                "sequence": 30,
                "can_be_sold": False,
            }
        )

    @classmethod
    def setUpClassPackaging(cls):
        cls.packaging_tu = cls.env["product.packaging"].create(
            {
                "name": "PACKAGING TU",
                "product_id": cls.product.id,
                "packaging_type_id": cls.packaging_type_tu.id,
                "qty": TU_PRODUCT_QTY,
            }
        )
        cls.packaging_pl = cls.env["product.packaging"].create(
            {
                "name": "PACKAGING PL",
                "product_id": cls.product.id,
                "packaging_type_id": cls.packaging_type_pl.id,
                "qty": PL_PRODUCT_QTY,
            }
        )
        cls.packaging_cannot_be_sold = cls.env["product.packaging"].create(
            {
                "name": "Test packaging cannot be sold",
                "product_id": cls.product.id,
                "qty": 10.0,
                "packaging_type_id": cls.packaging_type_cannot_be_sold.id,
            }
        )
        cls.sellable_packagings = cls.packaging_tu | cls.packaging_pl

    @classmethod
    def setUpClassSaleOrder(cls):
        cls.so_model = cls.env["sale.order"]
        sale_form = Form(cls.so_model)
        sale_form.partner_id = cls.partner
        with sale_form.order_line.new() as line:
            line.product_id = cls.product
            line.product_uom = cls.product.uom_id
        cls.order = sale_form.save()
        cls.order_line = cls.order.order_line
