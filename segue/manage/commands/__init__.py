from flask import Flask
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

import segue, segue.core

import populate
import boletos
import clean
import report

def _make_context():
    import segue.models
    return dict(app=app, db=segue.core.db, models=segue.models)


app = segue.Application()

migrate = Migrate(app, segue.core.db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command('shell', Shell(make_context=_make_context))

manager.command(populate.populate)
manager.command(populate.populate_reference_data)
manager.command(clean.clean_bad_buyers)
manager.command(boletos.process_boletos)
manager.command(report.buyers_report)
manager.command(report.caravan_report)
manager.command(report.import_caravan)
