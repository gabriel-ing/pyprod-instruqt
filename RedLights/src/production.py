from intersystems_pyprod import Production, ServiceItem, ProcessItem, OperationItem


iris_package_name = "RedLights"

class MyProduction(Production):
    
    actor_pool_size = 2

    services = [
        ServiceItem("FromCSV", "RedLights.FromCSV", 
                    host_settings={"target_config_name": "RoutingProcess"},
                    adapter_settings=
                        {"file_dir": "/home/irisowner/dev/RedLights/Data/IN/",
                         "archive_dir": "/home/irisowner/dev/RedLights/Data/OUT/"}
                    )
    ]

    processes = [
        ProcessItem("RoutingProcess", "RedLights.RoutingProcess", 
                    host_settings=
                        {"archive_target":"ArchiveOperation",
                         "ticket_target": "TicketOperation" # C4 add comma
                         # C4 Add Census Target Setting
                         }
                    )

    ]

    operations = [
        OperationItem("ArchiveOperation", "RedLights.ArchiveOperation"),
        OperationItem("TicketOperation", "RedLights.TicketOperation") # C4 Add Comma Here 
        # C4: Add Operation Item Here
    ]