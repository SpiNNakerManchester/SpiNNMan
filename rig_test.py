from rig.machine_control.machine_controller import MachineController
import time

machine = "192.168.240.253"
#machine = "spinn-10.cs.man.ac.uk"
mbs = 10.0

n_bytes = mbs * 1000.0 * 1000.0

start = float(time.time())

machine_controller = MachineController(machine)
machine_controller.read(0x70000000, int(n_bytes), 0, 0, 0)

end = float(time.time())
seconds = float(end - start)
speed = (mbs * 8) / seconds

print ("Read {} MB in {} seconds ({} Mb/s)".format(mbs, seconds, speed))
