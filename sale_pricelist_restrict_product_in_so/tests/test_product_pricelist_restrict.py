# -*- coding: utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tests.common import TransactionCase


class TestSearchProduct(TransactionCase):

    def create_browse(self, model, values):
        return model.browse(
            self.cr, self.uid,
            model.create(self.cr, self.uid, values))

    def setUp(self):
        super(TestSearchProduct, self).setUp()

        self.m_category = self.registry("product.category")
        self.m_product = self.registry("product.product")
        self.m_pricelist = self.registry("product.pricelist")
        self.m_pricelist_type = self.registry("product.pricelist.type")
        self.m_pricelist_version = self.registry("product.pricelist.version")
        self.m_pricelist_items = self.registry("product.pricelist.item")

        # Data we create:
        #   ProductA1    CatA
        #   ProdcuctA2   \- CatAA
        #   ProductB     CatB

        self.pl_pricetype = self.create_browse(self.m_pricelist_type,
                                               {"name": "test",
                                                "key": "test"})

        self.cat_a = self.create_browse(self.m_category, {"name": "CatA"})
        self.cat_aa = self.create_browse(self.m_category,
                                         {"name": "CatAA",
                                          "parent_id": self.cat_a.id})
        self.cat_b = self.create_browse(self.m_category, {"name": "CatB"})

        self.pr_a1 = self.create_browse(self.m_product,
                                        {"name": "ProductA1",
                                         "categ_id": self.cat_a.id,
                                         "price": 10.0})

        self.pr_a2 = self.create_browse(self.m_product,
                                        {"name": "ProductA2",
                                         "categ_id": self.cat_aa.id,
                                         "price": 15.0})

        self.pr_b = self.create_browse(self.m_product,
                                       {"name": "ProductB",
                                        "categ_id": self.cat_b.id,
                                        "price": 20.0})

    def test_restrict_product(self):
        plb = self.create_browse(self.m_pricelist, {
            "name": "PricelistPl",
            "version_id": [
                (0, 0, {"name": "PLV1",
                        "items_id": [
                            (0, 0, {"name": "PLV1P1",
                                    "product_id": self.pr_b.id,
                                    "base": 1,
                                    "price_discount": -0.5
                                    })]
                        })],
            "type": self.pl_pricetype.key,
        })
        self.assertItemsEqual(
            self.m_product.search(self.cr, self.uid, [],
                                  context={"pricelist": plb.id}),
            [self.pr_b.id],
            "Only Product B should be returned in context of pricelist A",
        )

    def test_restrict_category(self):
        pla = self.create_browse(self.m_pricelist, {
            "name": "PricelistPLA",
            "version_id": [
                (0, 0, {"name": "PLAV1",
                        "items_id": [
                            (0, 0, {"name": "PLAV1P1",
                                    "categ_id": self.cat_a.id,
                                    "base": 1,
                                    "price_discount": -1}),
                        ]})
            ],
            "type": self.pl_pricetype.key,
        })
        self.assertItemsEqual(
            self.m_product.search(self.cr, self.uid, [],
                                  context={"pricelist": pla.id}),
            [self.pr_a1.id, self.pr_a2.id],
            "Products A1 and A2 expected",
        )

    def test_restrict_both(self):
        pla = self.create_browse(self.m_pricelist, {
            "name": "PricelistPLA",
            "version_id": [
                (0, 0, {"name": "PLAV1",
                        "items_id": [
                            (0, 0, {"name": "PLAV1P1",
                                    "product_id": self.pr_a2.id,
                                    "categ_id": self.cat_a.id,
                                    "base": 1,
                                    "price_discount": -1}),
                        ]})
            ],
            "type": self.pl_pricetype.key,
        })
        self.assertItemsEqual(
            self.m_product.search(self.cr, self.uid, [],
                                  context={"pricelist": pla.id}),
            [self.pr_a2.id],
            "Products A1 and A2 expected",
        )
