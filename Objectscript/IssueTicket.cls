Class RedLights.TicketManager Extends %RegisteredObject
{   

    ClassMethod IssueTicket(license, severity) As %String
    {
        return "Issued ticket to License: "_license_" with severity: "_severity
    }


}
