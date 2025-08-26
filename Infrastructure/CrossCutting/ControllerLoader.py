import pkgutil
import importlib
import inspect
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRouter
from App.Controllers.ControllerBase import ControllerBase
from Domain.Models.ApplicationConfigurationModels.AppSettingsModel import AppSettingsModel
from Infrastructure.CrossCutting.InjectionConfiguration import AppContainer


class ControllerLoader:
    @staticmethod
    def custom_openapi(app: FastAPI, app_settings: AppSettingsModel):
        def openapi():
            if app.openapi_schema:
                return app.openapi_schema
            openapi_schema = get_openapi(
                title=app_settings.APP_NAME,
                version=str(app_settings.APP_VERSION),
                routes=app.routes,
            )
            app.openapi_schema = openapi_schema
            return openapi_schema
        #necessary to avoid circular import
        return openapi

    @staticmethod
    def auto_register_controllers(app: FastAPI, package: str = "App.Controllers"):
        package_module = importlib.import_module(package)
        package_path = package_module.__path__

        for _, module_name, _ in pkgutil.iter_modules(package_path):
            full_module_name = f"{package}.{module_name}"
            module = importlib.import_module(full_module_name)

            for name, cls in inspect.getmembers(module, inspect.isclass):
                if issubclass(cls, ControllerBase) and cls is not ControllerBase:
                    instance = cls()
                    if isinstance(getattr(instance, "router", None), APIRouter):
                        app.include_router(instance.router)

    @staticmethod
    def wire_all_controllers(package: str = "App.Controllers"):
        package_module = importlib.import_module(package)
        package_path = package_module.__path__

        modules_to_wire = []

        for _, module_name, is_pkg in pkgutil.iter_modules(package_path):
            full_module_name = f"{package}.{module_name}"
            modules_to_wire.append(full_module_name)

            if is_pkg:
                subpackage_module = importlib.import_module(full_module_name)
                subpackage_path = subpackage_module.__path__
                for _, submod_name, _ in pkgutil.iter_modules(subpackage_path):
                    modules_to_wire.append(f"{full_module_name}.{submod_name}")

        AppContainer().wire(modules=modules_to_wire)
