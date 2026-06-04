import iris
import iris_persistence
from iris_persistence import Field, Model
from datetime import datetime
iris_persistence.configure()

class Product(Model, persistent=True):
    intersection:str = Field()
    record_date:datetime.date = Field()
    record_time: datetime.time = Field()
    license_plate_number:str = Field()
    car_type:str = Field()
    num:int = Field()
    newfield:str = Field()
    
    class Meta:
        classname  = "New.ExtendedClassNew"
        mode = "extend"
        superclasses = "Ens.Request"

Product.sync_schema() 

product = Product()
product.intersection = "Main St and 1st Ave"
product.record_date = datetime.strptime("2023-01-01", "%Y-%m-%d").date()
product.record_time = datetime.strptime("12:00:00", "%H:%M:%S").time()
product.license_plate_number = "ABC123"
product.car_type = "Sedan"
product.save()


opened = Product.get(11)
print(opened)
print(type(opened.record_date))