import unittest
from spinnman.messages.sdp.sdp_flag import SDPFlag


class TestSDPEnums(unittest.TestCase):
    def test_sdp_flag(self):
        self.assertEquals(SDPFlag.REPLY_NOT_EXPECTED.value, 0x7)
        self.assertEquals(SDPFlag.REPLY_EXPECTED.value, 0x87)


if __name__ == '__main__':
    unittest.main()
