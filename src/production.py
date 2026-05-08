from intersystems_pyprod import (
    IRISLog,
    BusinessService,
    BusinessProcess,
    BusinessOperation,
    OutboundAdapter,
    InboundAdapter,
    IRISParameter,
    IRISProperty,
    Status
)
import time

class InboundFileAdapter(InboundAdapter):
    infile = IRISProperty("", "str", "Path to the file directory to watch", settings="FileAdapterSettings")

    working = IRISProperty("", "str", "Path of the directory where files are kept while processing is in progress.\
                            If left blank, the file will remain in the infile directory",
                            settings="FileAdapterSettings")
    
    archive = IRISProperty("", "str", "Path of the directory where files are moved after processing is complete",
                            settings="FileAdapterSettings")

    watch_time = IRISProperty(default=5, datatype="int", description="Time in milliseconds between checks for new files in the infile directory")

    def __init__(self, iris_host_object):
        super().__init__(iris_host_object)


    def OnTask(self):
        status = Status.OK()
        time.sleep(self.watch_time / 1000)


        return status  