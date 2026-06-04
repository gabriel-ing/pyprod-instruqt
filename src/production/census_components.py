import requests

from intersystems_pyprod import (
    BusinessOperation,
    IRISParameter,
    IRISProperty,
    Column,
    JsonSerialize,
    IRISLog,
    Status,
)


iris_package_name = "RedLights"

class CensusRequest(JsonSerialize):
    state:str = Column()
    county:str = Column()
    tract:str = Column()
    block_group:str = Column()

class CensusResponse(JsonSerialize):
    population:int = Column()

class ToCensus(BusinessOperation):

    message_map = {
        "RedLights.CensusRequest": "GetPopulation"
    }

    def GetPopulation(self, request):

        url = f"https://api.census.gov/data/2018/acs/acs5?get=NAME,B00001_001E&for=block%20group:{request.block_group}&in=state:{request.state}%20county:{request.county}%20tract:{request.tract}&key=6c59dddebe1002a5d5a9848e404e19e5f1614ce9"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            population = int(data[1][1])  # Extract population from response
            return Status.OK, CensusResponse(population=population)

        else: 
            IRISLog.Error(f"Census API request failed with status code: {response.status_code}")
            return Status.ERROR(f"Census API request failed with status code: {response.status_code}"), None
