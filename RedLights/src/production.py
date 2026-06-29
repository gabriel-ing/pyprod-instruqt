from intersystems_pyprod import Production, ServiceItem, ProcessItem, OperationItem


iris_package_name = "RedLights"

class MyProduction(Production):
    
    actor_pool_size = 2

    services = [
        ServiceItem("FromCSV", "RedLights.FromCSV", 
                    host_settings={"target_config_name": "RedLights.RoutingProcess"},
                    adapter_settings=
                        {"FILE_DIR": "/home/irisowner/dev/RedLights/Data/IN/",
                         "archive_dir": "/home/irisowner/dev/RedLights/Data/OUT/"}
                    )
    ]

    processes = [
        ProcessItem("RoutingProcess", "RedLights.RoutingProcess", 
                    host_settings=
                        {"archive_target":"ArchiveOperation",
                         "ticket_target": "TicketOperation",
                         "census_target": "CensusOperation"
                         }
                    )

    ]

    operations = [
        OperationItem("ArchiveOperation", "RedLights.ArchiveOperation"),
        OperationItem("TicketOperation", "RedLights.TicketOperation"),
        OperationItem("CensusOperation", "RedLights.CensusOperation")
    ]