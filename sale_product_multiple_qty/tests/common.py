# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import Form, TransactionCase


class SaleProductMultipleQtyCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Product = cls.env["product.product"]
        cls.UoM = cls.env["uom.uom"]
        cls.partner = cls.env["res.partner"].create({"name": "Test"})
        cls.base_uom = cls.env.ref("uom.product_uom_unit")
        cls.uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.product_notebook = cls._create_product("Notebook")
        cls.product_screw = cls._create_product("Screw")
        cls.product_table = cls._create_product("Table")
        cls.product_liquid = cls._create_product("Liquid")
        cls.uom_pack_100 = cls._create_uom("Pack of 100", 100, cls.base_uom)
        # We sell tables in packs of 10 and 100 units, multiple 100.
        cls.uom_pack_10 = cls._create_uom("Pack of 10", 10, cls.base_uom)
        cls.uom_nested_pack_100 = cls._create_uom(
            "Nested Pack of 100", 10, cls.uom_pack_10
        )
        # We sell notebooks in packs of 6 and 100 units, multiple 100.
        # 100 is NOT divisible by 6, so the result is rounded up to an integer.
        cls.uom_pack_6 = cls._create_uom("Pack of 6", 6, cls.base_uom)
        # We sell screws in packs of 5 and 100 units, multiple 100.
        cls.uom_pack_5 = cls._create_uom("Pack of 5", 5, cls.base_uom)
        cls.uom_box_250 = cls._create_uom("Box of 250", 250, cls.base_uom)
        cls.uom_box_500 = cls._create_uom("Box of 500", 500, cls.base_uom)
        cls.uom_400g = cls._create_uom("400g", 0.4, cls.uom_kg)
        cls.product_nested_box = cls._create_product("Nested Box", uom=cls.uom_pack_10)
        cls.product_big_box = cls._create_product("Big Box", uom=cls.uom_box_250)
        cls._configure_products()
        cls._create_sale_order()
        cls.nb_line, cls.screw_line, cls.table_line, cls.liquid_line = (
            cls.sale.order_line
        )
        cls.nb_line.write({"product_uom_id": cls.uom_pack_6.id})
        cls.screw_line.write({"product_uom_id": cls.uom_pack_5.id})
        cls.table_line.write({"product_uom_id": cls.uom_pack_10.id})
        cls.liquid_line.write({"product_uom_id": cls.uom_400g.id})

    @classmethod
    def _configure_products(cls):
        """Configure products with allowed UoMs and sales multiple UoMs."""
        cls.product_notebook.uom_ids = [
            Command.link(cls.uom_pack_6.id),
            Command.link(cls.uom_pack_100.id),
        ]
        cls.product_notebook.sale_multiple_uom_id = cls.uom_pack_100
        cls.product_screw.uom_ids = [
            Command.link(cls.uom_pack_5.id),
            Command.link(cls.uom_pack_100.id),
        ]
        cls.product_screw.sale_multiple_uom_id = cls.uom_pack_100
        cls.product_table.uom_ids = [
            Command.link(cls.uom_pack_10.id),
            Command.link(cls.uom_pack_100.id),
        ]
        cls.product_table.sale_multiple_uom_id = cls.uom_pack_100
        cls.product_liquid.uom_ids = [
            Command.link(cls.uom_400g.id),
        ]
        cls.product_liquid.sale_multiple_uom_id = cls.uom_kg
        cls.product_nested_box.uom_ids = [
            Command.link(cls.uom_nested_pack_100.id),
        ]
        cls.product_nested_box.sale_multiple_uom_id = cls.uom_nested_pack_100
        cls.product_big_box.uom_ids = [
            Command.link(cls.uom_box_500.id),
        ]
        cls.product_big_box.sale_multiple_uom_id = cls.uom_box_500

    @classmethod
    def _create_product(cls, name, uom=None):
        """Create a consumable product for sales multiple quantity tests.

        :param str name: name of the product to create.
        :param recordset uom: optional product default UoM.
        :return: created product variant.
        """
        vals = {"name": name, "type": "consu"}
        if uom:
            vals["uom_id"] = uom.id
        return cls.Product.create(vals)

    @classmethod
    def _create_uom(cls, name, factor, relative_uom_id):
        """Create a UoM using Odoo 19 relative UoM hierarchy fields.

        :param str name: name of the UoM to create.
        :param float factor: factor relative to ``relative_uom_id``.
        :param recordset relative_uom_id: parent UoM in the hierarchy.
        :return: created UoM.
        """
        return cls.UoM.create(
            {
                "name": name,
                "relative_factor": factor,
                "relative_uom_id": relative_uom_id.id,
            }
        )

    @classmethod
    def _create_sale_order(cls):
        """Create the shared sale order used by core rounding tests."""
        with Form(cls.env["sale.order"]) as sale:
            sale.partner_id = cls.partner
            with sale.order_line.new() as line:
                line.product_id = cls.product_notebook
            with sale.order_line.new() as line:
                line.product_id = cls.product_screw
            with sale.order_line.new() as line:
                line.product_id = cls.product_table
            with sale.order_line.new() as line:
                line.product_id = cls.product_liquid
        cls.sale = sale.save()

    def _create_order_line(self, product, uom=None):
        """Create a sale order with a single line for the given product.

        :param recordset product: product to set on the sale order line.
        :param recordset uom: optional UoM to force on the line.
        :return: created sale order line.
        """
        with Form(self.env["sale.order"]) as sale:
            sale.partner_id = self.partner
            with sale.order_line.new() as line:
                line.product_id = product
        sale_order = sale.save()
        line = sale_order.order_line
        if uom:
            line.product_uom_id = uom
        return line
