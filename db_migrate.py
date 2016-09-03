import imp
from migrate.versioning import api
from application import db
from config import SQLALCHEMY_DATABASE_URI as SDU
from config import SQLALCHEMY_MIGRATE_REPO as SMR

v = api.db_version(SDU, SMR)
migration = SMR + '/versions/{:03}_migration.py'.format(v+1)
tmp_module = imp.new_module('old_model')
old_model = api.create_model(SDU, SMR)
exec(old_model, tmp_module.__dict__)

script = api.make_update_script_for_model(
         SDU, SMR, tmp_module.meta, db.metadata)
open(migration, "wt").write(script)
api.upgrade(SDU, SMR)
v = api.db_version(SDU, SMR)

print('New migration saved as {}'.format(migration))
print('Current Database version: {}'.format(v))
