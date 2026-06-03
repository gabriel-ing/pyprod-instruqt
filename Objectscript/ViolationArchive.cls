Class RedLights.ViolationArchive Extends %Persistent
{
    Property ProcessDate As %Date;
    Property ProcessTime As %Time;
    Property Intersection As %String;
    Property LicensePlateNumber As %String;
    Property VehicleType As %String;
    Property EventDate As %Date;
    Property EventTime As %Time;
    Property Exempt As %Boolean;

Storage Default
{
<Data name="ViolationArchiveDefaultData">
<Value name="1">
<Value>%%CLASSNAME</Value>
</Value>
<Value name="2">
<Value>ProcessDate</Value>
</Value>
<Value name="3">
<Value>ProcessTime</Value>
</Value>
<Value name="4">
<Value>Intersection</Value>
</Value>
<Value name="5">
<Value>LicensePlateNumber</Value>
</Value>
<Value name="6">
<Value>CarType</Value>
</Value>
<Value name="7">
<Value>EventDate</Value>
</Value>
<Value name="8">
<Value>EventTime</Value>
</Value>
<Value name="9">
<Value>Exempt</Value>
</Value>
<Value name="10">
<Value>VehicleType</Value>
</Value>
</Data>
<DataLocation>^RedLights.ViolationArchiveD</DataLocation>
<DefaultData>ViolationArchiveDefaultData</DefaultData>
<IdLocation>^RedLights.ViolationArchiveD</IdLocation>
<IndexLocation>^RedLights.ViolationArchiveI</IndexLocation>
<StreamLocation>^RedLights.ViolationArchiveS</StreamLocation>
<Type>%Storage.Persistent</Type>
}

}
