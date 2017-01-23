import unittest
from spinn_machine.core_subsets import CoreSubset, CoreSubsets
from spinnman.exceptions import SpinnmanInvalidParameterException

class TestCoreSubsets(unittest.TestCase):
    def test_create_new_default_core_subsets(self):
        css = CoreSubsets()

    def test_create_new_core_subsets(self):
        proc_list = [0,1,2,3,5,8,13]
        cs = CoreSubset(0,0,proc_list)
        css = CoreSubsets([cs])
        self.assertIn(cs,css.core_subsets)
        for core_subset in css.core_subsets:
            self.assertIn(core_subset,[cs])

    def test_add_processor_duplicate_processor(self):
        proc_list = [0,1,2,3,5,8,13]
        cs = CoreSubset(0,0,proc_list)
        css = CoreSubsets([cs])
        css.add_processor(0,0,0)

    def test_add_processor_duplicate_processor_different_chip(self):
        proc_list = [0,1,2,3,5,8,13]
        cs = CoreSubset(0,0,proc_list)
        css = CoreSubsets([cs])
        css.add_processor(0,1,0)

    def test_add_core_subset_duplicate_core_subset(self):
        proc_list = [0,1,2,3,5,8,13]
        cs = CoreSubset(0,0,proc_list)
        css = CoreSubsets([cs])
        css.add_core_subset(cs)

    def test_add_core_subset(self):
        proc_list = [0,1,2,3,5,8,13]
        cs = CoreSubset(0,0,proc_list)
        css = CoreSubsets()
        css.add_core_subset(cs)
        self.assertIn(cs,css.core_subsets)
        for core_subset in css.core_subsets:
            self.assertIn(core_subset,[cs])

    def test_add_processor(self):
        proc_list = [0,1,2,3,5,8,13]
        cs = CoreSubset(0,0,proc_list)
        css = CoreSubsets()
        css.add_core_subset(cs)
        self.assertIn(cs,css.core_subsets)
        for core_subset in css.core_subsets:
            self.assertIn(core_subset,[cs])

if __name__ == '__main__':
    unittest.main()
