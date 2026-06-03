from intersystems_pyprod import Production, ServiceItem, ProcessItem, OperationItem


iris_package_name = "RedLights"

class MyProduction(Production):
    
    actor_pool_size = 2

    services = [
        ServiceItem("FromCSV", "RedLights.FromCSV", 
                    host_settings={"target_config_name": "RedLights.RoutingProcess"},
                    adapter_settings=
                        {"FILE_DIR": "/home/irisowner/dev/src/Data/In/",
                         "ARCHIVE_DIR": "/home/irisowner/dev/src/Data/Out/"}
                    )
    ]

    processes = [
        ProcessItem("RedLights.RoutingProcess", "RedLights.RoutingProcess", 
                    host_settings=
                        {"archive_target":"RedLights.ArchiveOperation",
                         "ticket_target": "RedLights.TicketOperation"}
                    )

    ]

    operations = [
        OperationItem("RedLights.ArchiveOperation", "RedLights.ArchiveOperation"),
        OperationItem("RedLights.TicketOperation", "RedLights.TicketOperation")
    ]