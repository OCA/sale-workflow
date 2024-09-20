# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from .common import TestPricelistCacheCommon


class TestPricelistCacheModels(TestPricelistCacheCommon):
    def test_get_parent_lists_tree(self):
        list0 = self.list0
        list1 = self.list1
        list2 = self.list2
        list3 = self.list3
        list4 = self.list4
        list5 = self.list5
        # list0 has no parent list, its tree should be itself only
        list0_parents_tree = list0._get_parent_list_tree()
        expected_list0_tree = list0
        self.assertEqual(list0_parents_tree, expected_list0_tree)
        # list1 parent is list0, tree should be list0|list1
        list1_parents_tree = list1._get_parent_list_tree()
        expected_list1_tree = expected_list0_tree | list1
        self.assertEqual(list1_parents_tree, expected_list1_tree)
        # list2 parent is list1, tree should be list0|list1|list2
        list2_parents_tree = list2._get_parent_list_tree()
        expected_list2_tree = expected_list1_tree | list2
        self.assertEqual(list2_parents_tree, expected_list2_tree)
        # list3 parent is list2, tree should be list0|list1|list2|list3
        list3_parents_tree = list3._get_parent_list_tree()
        expected_list3_tree = expected_list2_tree | list3
        self.assertEqual(list3_parents_tree, expected_list3_tree)
        # list4 parent is list0, tree should be list0|list4
        list4_parents_tree = list4._get_parent_list_tree()
        expected_list4_tree = expected_list0_tree | list4
        self.assertEqual(list4_parents_tree, expected_list4_tree)
        # list 5 parent is list3, tree should be list0|list1|list2|list3|list5
        list5_parents_tree = list5._get_parent_list_tree()
        expected_list5_tree = expected_list3_tree | list5
        self.assertEqual(list5_parents_tree, expected_list5_tree)

    def test_get_parent_pricelists(self):
        # test that list2 finds the parent pricelist list1
        self.assertEqual(self.list2._get_parent_pricelists(), self.list1)
        # test that list1 is not returned when item is expired
        item = self.list2.item_ids.filtered(
            lambda item: (
                item.applied_on == "3_global"
                and item.base == "pricelist"
                and item.base_pricelist_id
            )
        )
        item.write({"date_end": "2021-03-14"})
        self.assertFalse(self.list2._get_parent_pricelists())
