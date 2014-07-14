from spinnman.connections.udp_connection import UDPConnection
from spinnman.messages.scp.impl.scp_read_memory_request import SCPReadMemoryRequest
from spinnman.messages.scp.impl.scp_read_memory_response import SCPReadMemoryResponse

connection = UDPConnection(remote_host="spinn-10.cs.man.ac.uk")
request = SCPReadMemoryRequest(0, 0, 0x70000000, 256)
connection.send_scp_request(request)
response = SCPReadMemoryResponse()
connection.receive_scp_response(response)
