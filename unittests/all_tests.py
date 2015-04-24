"""
runs all spinnman tests scripts
"""
import unittest

testmodules = [
    'connection_tests.test_callback_queue',
    'connection_tests.test_connection_queue',
    'connection_tests.test_message_callback',
    'connection_tests.test_scp_listener',
    'connection_tests.test_udp_boot_connection',
    'connection_tests.test_udp_connection',
    'data_tests.test_big_endian_byte_array_byte_reader',
    'data_tests.test_big_endian_byte_array_byte_writer',
    'data_tests.test_file_data_reader',
    'data_tests.test_little_endian_byte_array_byte_reader',
    'data_tests.test_little_endian_byte_array_byte_writer',
    'data_tests.test_little_endian_data_reader_byte_reader',
    'model_tests.test_chip_info', 'model_tests.test_core_subset_model',
    'model_tests.test_core_subsets_model', 'model_tests.test_cpu_info',
    'model_tests.test_io_buff_model', 'model_tests.test_iptag_model',
    'model_tests.test_machine_dimensions_model',
    'model_tests.test_retrieving_values_from_enum_models',
    'model_tests.test_version_info_model',
    'scp_tests.test_count_state_request', 'scp_tests.test_count_state_response',
    'scp_tests.test_iptag_clear_request', 'scp_tests.test_iptag_set_request',
    'scp_tests.test_scp_application_run_request',
    'scp_tests.test_scp_check_ok_response', 'scp_tests.test_scp_enums',
    'scp_tests.test_scp_flood_fill_data_request',
    'scp_tests.test_scp_flood_fill_end_request',
    'scp_tests.test_scp_flood_fill_start_request',
    'scp_tests.test_scp_iptag_get_request',
    'scp_tests.test_scp_iptag_get_response',
    'scp_tests.test_scp_iptag_info_request',
    'scp_tests.test_scp_iptag_info_response',
    'scp_tests.test_scp_led_request', 'scp_tests.test_scp_link_request',
    'scp_tests.test_scp_link_response',
    'scp_tests.test_scp_message_assembly',
    'scp_tests.test_scp_read_memory_request',
    'scp_tests.test_scp_read_memory_response',
    'scp_tests.test_scp_response_header',
    'scp_tests.test_scp_router_alloc_request',
    'scp_tests.test_scp_router_alloc_response',
    'scp_tests.test_scp_version_request',
    'scp_tests.test_scp_version_response',
    'scp_tests.test_write_scp_request_header',
    'sdp_tests.test_sdp_enums',
    'sdp_tests.test_sdp_message_assembly',
    'threads_tests.scp_message_thread',
    'threads_tests.test_get_iptags_thread',
    'threads_tests.test_iobuf_thread',
    'test_boot_message_assembly',
    'test_multicast_message_assembly',
    'test_transceiver',
    'test_utils']

suite = unittest.TestSuite()

for t in testmodules:
    try:
        # If the module defines a suite() function, call it to get the suite.
        mod = __import__(t, globals(), locals(), ['suite'])
        suitefn = getattr(mod, 'suite')
        suite.addTest(suitefn())
    except (ImportError, AttributeError):
        # else, just load all the test cases from the module.
        suite.addTest(unittest.defaultTestLoader.loadTestsFromName(t))

unittest.TextTestRunner().run(suite)