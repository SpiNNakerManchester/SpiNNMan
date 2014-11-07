class CallbackWorker(object):

    @staticmethod
    def call_callback(callback, packet):
        callback(packet)



