from migrate.versioning import api
from config import SQLALCHEMY_DATABASE_URI as SDU
from config import SQLALCHEMY_MIGRATE_REPO as SMR

v = api.db_version(SDU, SMR)
api.downgrade(SDU, SMR, v - 1)
v = api.db_version(SDU, SMR)
print('Current database version: {}'.format(v))
