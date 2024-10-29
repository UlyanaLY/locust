from locust import LoadTestShape
from config.config import cfg, logger


class MyCustomLoadShape(LoadTestShape):
    match cfg.loadshape_type:
        case "baseline": 
            stages = [
                {"duration": 60, "users": 1, "spawn_rate": 5}
            ]
   

    def tick(self): # стандартная функция локаста, взятая из документации, для работы с кастомными "Лоад-Шейпами"
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                tick_data = (stage["users"], stage["spawn_rate"])
                return tick_data

        return None