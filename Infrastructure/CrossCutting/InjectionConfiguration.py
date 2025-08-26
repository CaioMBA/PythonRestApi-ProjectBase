from dependency_injector import containers, providers
from Domain.Utils import Utils
from Infrastructure.Data.Api.DefaultApiAccess import DefaultApiAccess
from Infrastructure.Data.Database.DefaultDatabaseAccess import DefaultDatabaseAccess


class AppContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    #region Extras
    utils = providers.Singleton(Utils)
    #endregion

    #region Database
    db_access = providers.Factory(DefaultDatabaseAccess, utils=utils)
    #endregion

    #region API
    api_access = providers.Factory(DefaultApiAccess, utils=utils)
    #endregion

