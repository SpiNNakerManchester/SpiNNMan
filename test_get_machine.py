from spinnman.processes.get_machine_process import GetMachineProcess
from spinnman.connections.udp_packet_connections.udp_spinnaker_connection import UDPSpinnakerConnection
get_machine_process = GetMachineProcess([UDPSpinnakerConnection(remote_host="spinn-8.cs.man.ac.uk")], None, None, None)

machine = get_machine_process.get_machine_details()
print machine
print machine.cores_and_link_output_string()
print get_machine_process._scp_request_sets[0].n_timeouts, "timeouts"
print get_machine_process._scp_request_sets[0].n_resent, "resent"
