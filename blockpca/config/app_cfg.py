
from tg.configuration import AppConfig

import blockpca
import transaction
import tg.predicates
from blockpca import model, lib
from blockpca.model.auth import User
from tg import request
from tgext.admin.tgadminconfig import BootstrapTGAdminConfig as TGAdminConfig

# Depot
from depot.manager import DepotManager

base_config = AppConfig()
base_config.renderers = []


base_config.disable_request_extensions = False


base_config.dispatch_path_translator = True

base_config.prefer_toscawidgets2 = True

base_config.package = blockpca


base_config.renderers.append('json')


base_config.renderers.append('kajiki')
base_config['templating.kajiki.strip_text'] = False 

base_config.default_renderer = 'kajiki'


base_config['session.enabled'] = True
base_config['session.data_serializer'] = 'json'
# Configure the base SQLALchemy Setup
base_config.use_sqlalchemy = True
base_config.model = blockpca.model
base_config.DBSession = blockpca.model.DBSession
# Configure the authentication backend
base_config.auth_backend = 'sqlalchemy'
# YOU MUST CHANGE THIS VALUE IN PRODUCTION TO SECURE YOUR APP
base_config.sa_auth.cookie_secret = "2a654f87-1cb4-43fb-834b-413c449a71a8"
# what is the class you want to use to search for users in the database
base_config.sa_auth.user_class = model.User

from tg.configuration.auth import TGAuthMetadata

# This tells to TurboGears how to retrieve the data for your user
class ApplicationAuthMetadata(TGAuthMetadata):
    def __init__(self, sa_auth):
        self.sa_auth = sa_auth

    def authenticate(self, environ, identity):
        login = identity['login']
        user = self.sa_auth.dbsession.query(self.sa_auth.user_class).filter_by(
            user_name=login
        ).first()

        if not user:
            display_name = identity.get('full_name', login)
            user = User(user_name=login, display_name=display_name)
            self.sa_auth.dbsession.add(user)
            self.sa_auth.dbsession.flush()
            transaction.commit()

        return login

    def get_user(self, identity, userid):
        return self.sa_auth.dbsession.query(self.sa_auth.user_class).filter_by(
            user_name=userid
        ).first()

    def get_groups(self, identity, userid):
        return [g.group_name for g in identity['user'].groups]

    def get_permissions(self, identity, userid):
        return [p.permission_name for p in identity['user'].permissions]

base_config.sa_auth.dbsession = model.DBSession

base_config.sa_auth.authmetadata = ApplicationAuthMetadata(base_config.sa_auth)

base_config['identity.allow_missing_user'] = False


base_config.sa_auth.form_plugin = None


base_config.sa_auth.post_login_url = '/post_login'

base_config.sa_auth.post_logout_url = '/post_logout'

base_config.sa_auth.translations = {
    "user_id": "id",
    "group_id": "id",
    "permission_id": "id",
}


class AdminConfig(TGAdminConfig):
    allow_only = tg.predicates.has_permission('admin')


base_config['depot.storage_path'] = "/tmp/depot"

# Configure default depot
tg.milestones.config_ready.register(
    lambda: DepotManager.configure('default', tg.config)
)

# Variable provider: this provides a default set of variables to the templating engine
def variable_provider():
    d = {}
    if request.identity:
        d['luser'] = request.identity['user']
    else:
        d['luser'] = None
    return d

base_config.variable_provider = variable_provider

# Task secheduler
def start_tgscheduler():
    import tgscheduler
    tgscheduler.start_scheduler()

    # TODO: Schedule some tasks here Jack

from tg.configuration import milestones
milestones.config_ready.register(start_tgscheduler)

try:
    # Enable DebugBar if available, install tgext.debugbar to turn it on
    from tgext.debugbar import enable_debugbar
    enable_debugbar(base_config)
except ImportError:
    pass
