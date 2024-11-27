# Подключение валидатора Pydantic
from pydantic import BaseModel
from pydantic.networks import IPvAnyAddress

# Валидация IP-адреса для подключения
class IpModel(BaseModel):
    ip: IPvAnyAddress