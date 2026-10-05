# TypeDict
from typing import TypedDict, Union, Optional, Any
dict = {"name":"vinoth","age":20}
dict["gender"]="M"

class Movie(TypedDict):
    name:str
    duration:float

movie1:Movie={"name":"GDN", "duration":20}

print(movie1)
print(dict)


def square(num:Union[int,float])->float:
    return num*num

def nice_message(msg:Optional[str])->str:
    if msg is None:
        return "some random message"
    else:
        return msg
    
square_lambd=lambda x:x*x    

nums=[1,2,3,4]

double_values=list(map(lambda num:num*2),nums)
