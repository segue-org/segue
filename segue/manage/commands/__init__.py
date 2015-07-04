from flask import Flask
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

import segue, segue.core

import populate
import boletos
import clean
import report
import judge
import notificate
import slotize
import import_caravan
import import_avulsos
import purchaser
import lister
import printer

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
manager.command(populate.populate_slots)
manager.command(clean.clean_bad_buyers)
manager.command(boletos.process_boletos)
manager.command(report.buyers_report)
manager.command(judge.invite_judges)
manager.command(judge.create_tournament)
manager.command(judge.tag_proposals)
manager.command(judge.put_tag_if_absent_of)
manager.command(judge.generate_round)
manager.command(judge.freeze_judging)
manager.command(notificate.notify_proposals)
manager.command(notificate.notify_slots)
manager.command(notificate.non_selection)
manager.command(report.adempiere_format)
manager.command(slotize.slotize)
manager.command(import_caravan.import_caravan)
manager.command(import_avulsos.import_avulsos)
manager.command(purchaser.ensure_purchase)
manager.command(lister.list_speakers)
manager.command(printer.bad_jobs)
manager.command(printer.good_jobs)
