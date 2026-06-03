Class RedLights.TicketManager Extends %RegisteredObject
{   

    ClassMethod IssueTicket(license) As %String
    {
        return "Issued ticket to License: "_license
    }


}
