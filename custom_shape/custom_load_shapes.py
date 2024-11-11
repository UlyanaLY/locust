from locust import LoadTestShape
from config.config import cfg, logger


class MyCustomLoadShape(LoadTestShape):
    match cfg.loadshape_type:
        case "baseline": 
            stages = [
                {"duration": 10, "users": 1, "spawn_rate": 1}
            ]

        case "fixedload": 
            stages = [
                {"duration": 300, "users": 10, "spawn_rate": 2}
            ]
            
        case "stages": 
            stages = [
                {"duration": 300, "users": 20, "spawn_rate": 2},
                {"duration": 600, "users": 40, "spawn_rate": 2},
                {"duration": 900, "users": 60, "spawn_rate": 2},
                {"duration": 1200, "users": 80, "spawn_rate": 2},
                {"duration": 1500, "users": 100, "spawn_rate": 2}
            ]                  

    def tick(self): # стандартная функция локаста, взятая из документации, для работы с кастомными "Лоад-Шейпами"
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                tick_data = (stage["users"], stage["spawn_rate"])
                return tick_data

        return None