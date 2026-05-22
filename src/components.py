from datetime import datetime
import time
import random

from intersystems_pyprod import (
    IRISParameter,
    IRISProperty,
    InboundAdapter,
    BusinessService,
    BusinessProcess,
    BusinessOperation,
    OutboundAdapter,
    Column,
    JsonSerialize,
    PickleSerialize,
    IRISLog,
    Status,
    debug_host,
)
from io import StringIO
import iris

iris_package_name = "RedLights"


class RedLightMessage(JsonSerialize):
    intersection:str = Column()
    record_date:datetime.date = Column()
    record_time: datetime.time = Column()
    license_plate_number:str = Column()
    car_type:str = Column()
    exempt:bool = Column()




class CSVReaderService(BusinessService):
    ADAPTER: str = IRISParameter(value="EnsLib.File.InboundAdapter", description="Full name of ADAPTER as would appear in the backend")

    target_config_name: str = IRISParameter(value="RedLight.FilterProcess", description="Name of the target configuration to send the message to")

    def OnProcessInput(self, pInput):
        # IRISLog.Info(f"Processing file: {pInput}")
        IRISLog.Info(f"Processing file: {type(pInput)}")
        # Convert it into a Python file-like object
        while not pInput.AtEnd: 
            out = pInput.ReadLine()
            IRISLog.Info(f"Read line: {out}")
            message = out.split(",")
            if len(message) == 5:
                red_light_message = RedLightMessage(
                    intersection=message[0],
                    record_date=datetime.strptime(message[1], "%Y-%m-%d").date(),
                    record_time=datetime.strptime(message[2], "%H:%M:%S").time(),
                    license_plate_number=message[3],
                    car_type=message[4]
                )
                self.SendRequestASync(self.target_config_name, red_light_message)

        return Status.OK


class RoutingProcess(BusinessProcess):
    archive_target: str = IRISParameter(value="RedLight.ArchiveOperation", description="Name of the target configuration to send the message to")
    ticket_target: str = IRISParameter(value="RedLight.TicketOperation", description="Name of the target configuration to send the message to")
    def OnRequest(self, request):
        IRISLog.Info(f"Received message in Business Process: {request}")
        
        archive_request = RedLightMessage(
            intersection=request.intersection,
            record_date=request.record_date,
            record_time=request.record_time,
            license_plate_number=request.license_plate_number,
            car_type=request.car_type
        )

        if request.car_type in ["police", "emergency", "ambulance"]:
            archive_request.exempt = True
            self.send_request_async(self.archive_target, archive_request)
            IRISLog.Info(f"Message is from an emergency vehicle, skipping: {request}")
            return Status.OK
        else: 
            ticket_operation_request = RedLightMessage(
                intersection=request.intersection,
                record_date=request.record_date,
                record_time=request.record_time,
                license_plate_number=request.license_plate_number,
                car_type=request.car_type
            )
            output = self.SendRequestSync(self.ticket_target, ticket_operation_request)
            if output != Status.OK:
                IRISLog.Error(f"Failed to send message to Business Operation: {ticket_operation_request}")
        
            archive_operation_request = RedLightMessage(
                intersection=request.intersection, 
                record_date=request.record_date,
                record_time=request.record_time,
                license_plate_number=request.license_plate_number,
                car_type=request.car_type
            )
            output = self.SendRequestSync(self.archive_target, archive_operation_request)

            archive_request.exempt = False
            self.send_request_async(self.archive_target, archive_request)
        return Status.OK
    
class TicketOperation(BusinessOperation):
    MessageMap = {
        f"{iris_package_name}.RedLightMessage": "issue_ticket"
    }
    def issue_ticket(self, request):
        IRISLog.Info(f"Received message in Business Operation: {request}")
        # Here you would have logic to create a ticket in your system. For this example, we'll just log it.
        IRISLog.Info(f"Creating ticket for red light violation: {request}")
        return Status.OK
    
class ArchiveOperation(BusinessOperation):
    MessageMap = {
        f"{iris_package_name}.RedLightMessage": "log_violation_to_archive"
    }
    def log_violation_to_archive(self, request):
        IRISLog.Info(f"Received message in Archive Operation: {request}")
        try: 
            
            dates = self._get_dates(request)

            violation = iris.RedLights.ViolationArchive._New()
            violation.Intersection = request.intersection
            violation.EventDate = dates["event_date"]
            violation.EventTime = dates["event_time"]
            violation.LicensePlateNumber = request.license_plate_number
            violation.CarType = request.car_type
            violation.ProcessDate = dates["process_date"]
            violation.ProcessTime = dates["process_time"]
            status = violation._Save()
            if status != 1:
                raise Exception("Failed to save violation to archive")
        except Exception as e:
            IRISLog.Error(f"Failed to archive message: {request}, error: {str(e)}")
            return Status.ERROR
        IRISLog.Info(f"Archiving message: {request}")
        return Status.OK
    
    def _get_dates(self, request):
        process_date = datetime.now().date().strftime("%Y-%m-%d")
        process_time = datetime.now().time().strftime("%H:%M:%S")

        event_date = datetime.strptime(request.record_date, "%d/%m/%Y").date().strftime("%Y-%m-%d")
        event_time = datetime.strptime(request.record_time, "%H:%M:%S").time().strftime("%H:%M:%S")
        
        
        return {"process_date": iris._Library.Date.OdbcToLogical(process_date), 
                "process_time": iris._Library.Time.OdbcToLogical(process_time), 
                "event_date": iris._Library.Date.OdbcToLogical(event_date), 
                "event_time": iris._Library.Time.OdbcToLogical(event_time)}