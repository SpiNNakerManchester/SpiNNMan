import unittest
from spinn_machine.core_subset import CoreSubset
from spinnman.exceptions import SpinnmanInvalidParameterException

class TestCoreSubset(unittest.TestCase):
    def test_create_new_core_subset(self):
        proc_list = [0,1,2,3,5,8,13]
        cs = CoreSubset(0,0,proc_list)
        self.assertEqual(cs.x,0)
        self.assertEqual(cs.y,0)
        for proc in cs.processor_ids:
            self.assertIn(proc, proc_list)
        self.assertEqual(len([x for x in cs.processor_ids]),len(proc_list))

    def test_create_new_core_subset_duplicate_processors(self):
        CoreSubset(0,0,[0,1,1,2,3,5,8,13])


    def test_create_empty_core_subset_add_processor(self):
        proc_list = [0,1,2,3,5,8,13]
        cs = CoreSubset(0,0,[])
        self.assertEqual(cs.x,0)
        self.assertEqual(cs.y,0)
        for proc in proc_list:
            cs.add_processor(proc)
        for proc in cs.processor_ids:
            self.assertIn(proc, proc_list)
        self.assertEqual(len([x for x in cs.processor_ids]),len(proc_list))



if __name__ == '__main__':
    unittest.main()
