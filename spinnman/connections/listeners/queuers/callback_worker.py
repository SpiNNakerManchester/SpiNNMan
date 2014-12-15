class CallbackWorker(object):

    @staticmethod
    def call_callback(callback, packet):
        try:
            callback(packet)
        except Exception as e:
            print "Packet Callback Error:{}".format(e)
