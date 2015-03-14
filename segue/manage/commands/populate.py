 # -*- coding: utf-8 -*-
from segue.core import db
from tests.support.factories import *
from segue.models import Account, Proposal, ProposalInvite, Track

def populate(clean=False):
    if clean:
        ProposalInvite.query.delete()
        Proposal.query.delete()
        Account.query.delete()
        populate_reference_data(True)

    accounts = [
        ValidAccountFactory.build(password='1234'),
        ValidAccountFactory.build(password='1234'),
        ValidAccountFactory.build(password='1234'),
    ]
    proposals = [
        ValidProposalFactory.build(owner=accounts[0]),
        ValidProposalFactory.build(owner=accounts[0]),
        ValidProposalFactory.build(owner=accounts[1]),
        ValidProposalFactory.build(owner=accounts[1]),
    ]
    proposal_invites = [
        ValidInviteFactory.build(proposal=proposals[0]),
        ValidInviteFactory.build(proposal=proposals[0]),
        ValidInviteFactory.build(proposal=proposals[0]),
    ]

    db.session.add_all(accounts)
    db.session.add_all(proposals)
    db.session.add_all(proposal_invites)
    db.session.commit()

def populate_reference_data(clean=False):
    if clean:
        Track.query.delete()

    tracks   = _build_tracks()
    products = _build_products()

    if not Track.query.all():   db.session.add_all(tracks)
    if not Product.query.all(): db.session.add_all(products)

    db.session.commit()

def _build_products():
    return [
        ValidProductFactory(kind="ticket", category="student", description="ingresso FISL16 - estudante - lote 1",  sold_until="2015-03-30 23:59:59", price=60 ),
        ValidProductFactory(kind="ticket", category="normal",  description="ingresso FISL16 - individual - lote 1", sold_until="2015-03-30 23:59:59", price=120),

        ValidProductFactory(kind="ticket", category="student", description="ingresso FISL16 - estudante - lote 2",  sold_until="2015-04-13 23:59:59", price=85 ),
        ValidProductFactory(kind="ticket", category="normal",  description="ingresso FISL16 - individual - lote 2", sold_until="2015-04-13 23:59:59", price=170),

        ValidProductFactory(kind="ticket", category="student", description="ingresso FISL16 - estudante - lote 3",  sold_until="2015-05-11 23:59:59", price=110),
        ValidProductFactory(kind="ticket", category="normal",  description="ingresso FISL16 - individual - lote 3", sold_until="2015-05-11 23:59:59", price=220),

        ValidProductFactory(kind="ticket", category="student", description="ingresso FISL16 - estudante - lote 4",  sold_until="2015-06-08 23:59:59", price=135),
        ValidProductFactory(kind="ticket", category="normal",  description="ingresso FISL16 - individual - lote 4", sold_until="2015-06-08 23:59:59", price=270),

        ValidProductFactory(kind="ticket", category="student", description="ingresso FISL16 - estudante - lote 5",  sold_until="2015-06-30 23:59:59", price=160),
        ValidProductFactory(kind="ticket", category="normal",  description="ingresso FISL16 - individual - lote 5", sold_until="2015-06-30 23:59:59", price=320),
    ]

def _build_tracks():
    return [
        #Zona Administração
        ValidTrackFactory(name_pt='Administração - Administração de Sistemas',
                          name_en='Administration - Systems Administration'),

        ValidTrackFactory(name_pt='Administração - Bancos de Dados',
                          name_en='Administration - Databases'),

        ValidTrackFactory(name_pt='Administração - Sistemas operacionais',
                          name_en='Administration - Operating Systems'),

        ValidTrackFactory(name_pt='Administração - Segurança',
                          name_en='Administration - Security'),

        #Zona Desenvolvimento
        ValidTrackFactory(name_pt='Desenvolvimento - Ferramentas, Metodologias e Padrões',
                          name_en='Development - Tools, Methodologies and Standards'),

        ValidTrackFactory(name_pt='Desenvolvimento - Gerência de Conteúdo / CMS',
                          name_en='Development - Content Management / CMS'),

        ValidTrackFactory(name_pt='Desenvolvimento - Linguagens de programação',
                          name_en='Development - Programming Languages'),

        #Zona Desktop
        ValidTrackFactory(name_pt='Desktop - Aplicações Desktop',
                          name_en='Desktop - Desktop Applications'),

        ValidTrackFactory(name_pt='Desktop - Multimídia',
                          name_en='Desktop - Multimedia'),

        ValidTrackFactory(name_pt='Desktop - Jogos',
                          name_en='Desktop - Games'),

        ValidTrackFactory(name_pt='Desktop - Distribuições',
                          name_en='Desktop - Distros'),

        #Zona Ecossistema
        ValidTrackFactory(name_pt='Ecossistema - Cultura, Filosofia, e Política',
                          name_en='Ecosystem - Culture, Philosophy, and Politics'),

        ValidTrackFactory(name_pt='Ecossistema - Negócios, Migrações e Casos',
                          name_en='Ecosystem - Business, Migrations and Cases'),

        #Zona Educação
        ValidTrackFactory(name_pt='Educação - Inclusão Digital',
                          name_en='Education - Digital Inclusion'),

        ValidTrackFactory(name_pt='Educação - Educação',
                          name_en='Education - Education'),

        #Zona Encontros Comunitários
        ValidTrackFactory(name_pt='Encontros Comunitários - Principal',
                          name_en='Community Meetings - Main'),

        ValidTrackFactory(name_pt='Encontros Comunitários - ASL',
                          name_en='Community Meetings - ASL'),

        ValidTrackFactory(name_pt='Encontros Comunitários - WSL',
                          name_en='Community Meetings - WSL'),

        #Zona Tópicos Emergentes
        ValidTrackFactory(name_pt='Tópicos Emergentes - Hardware Aberto',
                          name_en='Trending Topics - Open Hardware'),

        ValidTrackFactory(name_pt='Tópicos Emergentes - Dados Abertos',
                          name_en='Trending Topics - Open Data'),

        ValidTrackFactory(name_pt='Tópicos Emergentes - Acesso Aberto',
                          name_en='Trending Topics - Open Access'),

        ValidTrackFactory(name_pt='Tópicos Emergentes - Governança da Internet',
                          name_en='Trending Topics - Internet Governance'),

        ValidTrackFactory(name_pt='Tópicos Emergentes - Privacidade e Vigilância',
                          name_en='Trending Topics - Privacy and Surveillance'),

        ValidTrackFactory(name_pt='Tópicos Emergentes - Energia Livre',
                          name_en='Trending Topics - Free Energy'),
    ]

