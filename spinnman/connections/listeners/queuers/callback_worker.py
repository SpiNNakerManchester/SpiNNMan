import traceback


class CallbackWorker(object):

    @staticmethod
    def call_callback(callback, packet):
        try:
            callback(packet)
        except Exception as e:
            traceback.print_exc()
            print "Packet Callback Error:{}".format(e)
