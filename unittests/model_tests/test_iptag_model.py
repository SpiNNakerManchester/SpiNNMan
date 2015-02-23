import unittest

from spinn_machine.tags.iptag import IPTag


class TestIptag(unittest.TestCase):
    def test_new_iptag(self):
        ip = "8.8.8.8"
        port = 1337
        tag = 255
        iptag = IPTag(ip, port, tag)
        self.assertEqual(ip, iptag.address)
        self.assertEqual(port, iptag.port)
        self.assertEqual(tag, iptag.tag)


if __name__ == '__main__':
    unittest.main()
