import requests

from intersystems_pyprod import (
    BusinessOperation,
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
        "RedLights.CensusRequest": "get_population"
    }

    def get_population(self, request):
        """
        Method to query the US Census API for population data based on the geographic information 
        provided in the request. The response from the API is used to determine the severity of 
        the red light violation based on the population of the area where the violation occurred.
        """
        
        # Define URL
        url = f"https://api.census.gov/data/2018/acs/acs5?get=NAME,B00001_001E&for=block%20group:{request.block_group}&in=state:{request.state}%20county:{request.county}%20tract:{request.tract}&key=6c59dddebe1002a5d5a9848e404e19e5f1614ce9"
        
        # Send GET Request
        response = requests.get(url)
        
        if response.status_code == 200:

            # Extract population from response
            data = response.json()
            population = int(data[1][1])  
            
            # Return status and response message
            return Status.OK(), CensusResponse(population=population)


        ## Handle error response
        else: 
            IRISLog.Error(f"Census API request failed with status code: {response.status_code}")
            return Status.ERROR(f"Census API request failed with status code: {response.status_code}"), None
