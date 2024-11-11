import logging
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import BaseModel, Field

class ScenarioConfig(BaseModel):
    included: bool
    weight: int

class WebToursBaseScenarioConfig(ScenarioConfig):
    ...

class WebToursCancelScenarioConfig(ScenarioConfig):
    ...

class Config(BaseSettings):
    locust_locustfile: str = Field("./locustfile.py", env="LOCUST_LOCUSTFILE")
    url: str = Field("http://localhost:1080", env="URL")
    loadshape_type: str = Field("baseline", env="LOADSHAPE_TYPE")
    webtours_base: WebToursBaseScenarioConfig
    webtours_cancel: WebToursCancelScenarioConfig
    pacing: int = Field(5, env="PACING")
    csv_url: str = Field("./test_data.csv", env="CSV_URL") 


class LogConfig():
    logger = logging.getLogger('demo_logger')
    logger.setLevel('DEBUG')
    file = logging.FileHandler(filename='test_logs.log')
    file.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    logger.addHandler(file)
    logger.propagate = False

env_file = Path(__file__).resolve().parent.parent / ".env"

cfg = Config(_env_file=(env_file if env_file.exists() else None), _env_nested_delimiter="__") # инициализация конфига

logger = LogConfig().logger # инициализация логгера