Class RedLights.NewProduction Extends Ens.Production
{

XData ProductionDefinition
{
<Production Name="RedLights.NewProduction" TestingEnabled="true" LogGeneralTraceEvents="false">
  <Description></Description>
  <ActorPoolSize>2</ActorPoolSize>
  <Item Name="RedLights.TicketOperation" Category="" ClassName="RedLights.TicketOperation" PoolSize="1" Enabled="true" Foreground="false" Comment="" LogTraceEvents="false" Schedule="">
  </Item>
  <Item Name="RedLights.ArchiveOperation" Category="" ClassName="RedLights.ArchiveOperation" PoolSize="1" Enabled="true" Foreground="false" Comment="" LogTraceEvents="false" Schedule="">
  </Item>
  <Item Name="RedLights.RoutingProcess" Category="" ClassName="RedLights.RoutingProcess" PoolSize="1" Enabled="true" Foreground="false" Comment="" LogTraceEvents="false" Schedule="">
  </Item>
  <Item Name="RedLights.CSVReaderService" Category="" ClassName="RedLights.CSVReaderService" PoolSize="1" Enabled="true" Foreground="false" Comment="" LogTraceEvents="false" Schedule="">
  </Item>
</Production>
}

}
