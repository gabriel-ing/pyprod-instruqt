from datetime import datetime
import os
import csv

from intersystems_pyprod import (
    IRISParameter,
    IRISProperty,
    InboundAdapter,
    BusinessService,
    BusinessProcess,
    BusinessOperation,
    Column,
    JsonSerialize,
    IRISLog,
    Status,
)
import iris


iris_package_name = "RedLights"

class RedLightMessage(JsonSerialize):
    # Basic record info 
    intersection:str = Column()
    record_date:str = Column()
    record_time:str = Column()
    license_plate_number:str = Column()
    vehicle_type:str = Column()

    exempt:bool = Column(default=0) # This field will be used to indicate whether the violation is exempt from ticketing (e.g. for emergency vehicles)
    severity:str = Column(default="unknown") # This field can be used to indicate the severity of the violation, which could be used for routing or ticketing decisions in a more complex implementation
    # Geographic information
    state:str = Column(default="")
    county:str = Column(default="")
    tract:str = Column(default="")
    block_group:str = Column(default="")



class CSVReaderAdapter(InboundAdapter):
        
    FILE_DIR: str = IRISProperty(description="Directory to monitor for new CSV files", settings="Adapter Settings")
    ARCHIVE_DIR: str = IRISProperty(description="Directory to move processed CSV files to", settings="Adapter Settings")

    def __init__(self, iris_host_object):
        super().__init__(iris_host_object)
        self.processed_files = {}

    def on_task(self): 
        '''
        Inbound CSV Reader adapter monitors a directory 
        '''

        i = 0
        # Loop in case files are skipped
        while True:
            
            # Get CSV files in directory
            files = self._list_csvs()
            
            # If no files are found, return OK and await next task execution 
            if not files:
                return Status.OK()
            
            # Process the first file
            filename = files[i]
            
            # Skip files which previously errored
            if filename in self.processed_files:
                    if self.processed_files[filename][:5] == "ERROR":
                        IRISLog.Info(f"Skipping previously failed file: {filename}")
                        i += 1
                        continue

            
            file_path = os.path.join(self.FILE_DIR, filename)
            IRISLog.Info(f"Found new file to process: {file_path}")
            try: 
                # Read CSV file 
                with open(file_path, newline='') as csvfile:
                    rows = list(csv.DictReader(csvfile))
                
                # Send the CSV file to Parent Business Service
                input = {"filename": filename, "rows": rows}
                self.business_host_process_input(input)

                # Add the file to the processed files dictionary 
                self.processed_files[filename] = f"PROCESSED {datetime.now()}"

                filename = filename+"."+datetime.now().strftime("%Y%m%d%H%M%S")

                # Move processed file to archive directory
                os.rename(file_path, os.path.join(self.ARCHIVE_DIR, filename))

                IRISLog.Info(f"Finished processing file: {file_path}, moved to archive.")

                return Status.OK()
                
            # Handle error and add to processed files dictionary to avoid reprocessing until issue is resolved
            except Exception as e:
                self.processed_files[filename] = f"ERROR {datetime.now()}"
                IRISLog.Error(f"Failed to process file: {file_path}, error: {str(e)}")
                return Status.ERROR(f"Failed to process file {filename}: {str(e)}")

    def _list_csvs(self):
        """Helper method to list CSV files in the FILE_DIR directory"""
        csvs =  [f for f in os.listdir(self.FILE_DIR) if f.endswith(".csv")]
        return csvs


class FromCSV(BusinessService):
    ## Challenge 3 
    ## TODO 3

    # Define adapter for service
    ADAPTER: str = IRISParameter(value="RedLights.CSVReaderAdapter", description="Full name of ADAPTER as would appear in the backend")
    
    # Define the target host for messages to be sent to 
    target_config_name: str = IRISProperty(description="Name of the target configuration to send the message to", settings="Target Settings")

    def on_process_input(self, input):
        """
        This method receives the CSV file from the Inbound Adapter and sends messages for each row. 
        """
        try: 
            IRISLog.Info(f"Processing file: {input['filename']} with {len(input['rows'])} rows")

            # Read the file dictionary taken from the adapter 
            for row in input["rows"]:
                    
                    # For each row, create a message
                    red_light_message = RedLightMessage(
                        intersection=row["ADDRESS"],
                        record_date=row["RECORD_DATE"],
                        record_time=row["RECORD_TIME"],
                        license_plate_number=row["LICENSE"],
                        vehicle_type=row["VEHICLE_TYPE"] ## Add a comma here 

                        ## Add Lines Here 
                    )

                    # Send to Business Process for filtering and routing
                    self.send_request_async(self.target_config_name, red_light_message)

            return Status.OK()
        except Exception as e:
            IRISLog.Error(f"Failed to process file: {input['filename']}, error: {str(e)}")
            return Status.ERROR(f"Failed to process file {input['filename']}: {str(e)}")

class RoutingProcess(BusinessProcess):
    archive_target: str = IRISProperty(description="Name of the target configuration to send the message to",settings="Target Settings")
    ticket_target: str = IRISProperty(description="Name of the target configuration to send the message to", settings="Target Settings")
    
    ## Challenge 3
    ## TODO 1 
    ## Add census target here 

    def on_request(self, request):

        # Prepare archive request message
        archive_request = RedLightMessage(
            intersection=request.intersection,
            record_date=request.record_date,
            record_time=request.record_time,
            license_plate_number=request.license_plate_number,
            vehicle_type=request.vehicle_type
        )


        # Skip ticketing for emergency vehicles, but still archive the violation
        if request.vehicle_type in ["police", "emergency", "ambulance"]:
            archive_request.exempt = 1
            # Send archive request asynchronously since we don't need to wait for it to complete
            self.send_request_async(self.archive_target, archive_request, response_required=0)

            IRISLog.Info(f"Message is from an emergency vehicle, skipping: {request}")
            return Status.OK()
        
        else: 
            # Create ticket operation request
            ticket_operation_request = RedLightMessage(
                intersection=request.intersection,
                record_date=request.record_date,
                record_time=request.record_time,
                license_plate_number=request.license_plate_number,
                vehicle_type=request.vehicle_type
            )

            ## Challenge 3
            ## TODO #2
            ## Add Census Call IF block here #### 
            ## if all([...) 

            # Send ticket request Synchronously since we want to ensure the ticket is issued before archiving the violation
            status, response = self.send_request_sync(self.ticket_target, ticket_operation_request)

            if status != Status.OK():
                IRISLog.Error(f"Failed to send message to Business Operation: {ticket_operation_request},\
                               Error Message:{iris.check_status(status)}")

            # Set exempt to False for non-emergency vehicles, but and archive violation
            archive_request.exempt = 0
            self.send_request_async(self.archive_target, archive_request,response_required=0)
        return Status.OK()
    
    def on_response(self, request, response, call_request, call_response, completion_key):
        return Status.OK()
    
    def _determine_severity(self, population):
        if population > 500:
            return "High"
        elif population > 250:
            return "Medium"
        else:
            return "Low"

class TicketOperation(BusinessOperation):
    MessageMap = {
        f"{iris_package_name}.RedLightMessage": "issue_ticket"
    }
    def issue_ticket(self, request):
        
        
        if not hasattr(request, "severity"):
            request.severity = "unknown"

        issue_ticket_status = iris.RedLights.TicketManager.IssueTicket(request.license_plate_number, request.severity)
        IRISLog.Info(issue_ticket_status)
    
        return Status.OK()
    
class ArchiveOperation(BusinessOperation):
    MessageMap = {
        f"{iris_package_name}.RedLightMessage": "log_violation_to_archive"
    }
    def log_violation_to_archive(self, request):

        try: 
            dates = self._get_dates(request)

            query = """INSERT INTO iris.RedLights.ViolationArchive
                        (
                            Intersection,
                            EventDate,
                            EventTime,
                            LicensePlateNumber,
                            VehicleType,
                            ProcessDate,
                            ProcessTime
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)"""

            stmt = iris.sql.prepare(query)

            sql_status = stmt.execute(
                request.intersection,
                dates["event_date"],
                dates["event_time"],
                request.license_plate_number,
                request.vehicle_type,
                dates["process_date"],
                dates["process_time"]
                )
            

        except Exception as e:
            IRISLog.Error(f"Failed to archive message: {request}, error: {str(e)}")
            return Status.ERROR(f"Failed to archive violation: {str(e)}")

        return Status.OK()
    
    def _get_dates(self, request):
        process_date = datetime.now().date().strftime("%Y-%m-%d")
        process_time = datetime.now().time().strftime("%H:%M:%S")

        event_date = datetime.strptime(request.record_date, "%m/%d/%Y").date().strftime("%Y-%m-%d")
        event_time = datetime.strptime(request.record_time, "%H:%M:%S").time().strftime("%H:%M:%S")
        
        
        return {"process_date": iris._Library.Date.OdbcToLogical(process_date), 
                "process_time": iris._Library.Time.OdbcToLogical(process_time), 
                "event_date": iris._Library.Date.OdbcToLogical(event_date), 
                "event_time": iris._Library.Time.OdbcToLogical(event_time)}