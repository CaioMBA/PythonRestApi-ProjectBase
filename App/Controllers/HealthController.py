from dependency_injector.wiring import Provide
from fastapi.params import Depends

from App.Controllers.ControllerBase import ControllerBase
from Domain.Models.ApplicationConfigurationModels.HealthReportModel import HealthReportModel
from Services.ApplicationServices.HealthCheckServices import HealthCheckServices


class HealthController(ControllerBase):
    def __init__(self):
        super().__init__()

        @self.router.get("/", response_model=HealthReportModel)
        async def root(service: HealthCheckServices= Depends(HealthCheckServices)):
            return await service.check()