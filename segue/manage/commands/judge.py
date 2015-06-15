# encoding: utf-8

from segue.mailer import MailerService
from segue.judge.services import JudgeService, TournamentService, RankingService
from segue.judge.errors import JudgeAlreadyExists
from segue.proposal.services import ProposalService
from support import *;

def invite_judges(filename, count=5, tid=0):
    init_command()
    content = open(filename, 'r').read()

    judge_service = JudgeService()
    mailer_service = MailerService()

    for entry in content.split("\n"):
        if not len(entry): continue
        print "{}creating token for {}{}{}...".format(F.RESET, F.GREEN, entry, F.RESET),
        try:
            token = judge_service.create_token(entry, count, tid)
            print "hash is {}{}{}, sending email...".format(F.GREEN, token.hash, F.RESET),
            mailer_service.invite_judge(token)
            print "OK"
        except JudgeAlreadyExists, e:
            print F.RED + "already exists!" + F.RESET

def generate_round(tid=0):
    init_command()

    service = TournamentService()
    print "generating round for tournament {}{}{}...".format(F.GREEN, tid, F.RESET)
    service.generate_round(tid)
    print "OK"

def freeze_judging(tid=0, aid=0):
    init_command()
    service = RankingService()
    r = service.classificate(tid, track_id=aid)
    for e in r:
        print e.rank, e.proposal.id, e.tag_names

def create_tournament(selection="*"):
    init_command()

    service = TournamentService()
    tournament = service.create_tournament(selection)

    print F.GREEN, "created tournament {} with selection {}".format(tournament.id, tournament.selection)

def tag_proposals(filename, tag_name):
    init_command()

    content = open(filename, 'r').read()
    affected = 0

    proposals = ProposalService()
    print "tagging proposals from file {}{}{} with {}{}{}".format(F.GREEN, filename, F.RESET, F.GREEN, tag_name, F.RESET)

    for line in content.split("\n"):
        if not len(line): continue
        pid = line.split(",")[0]
        proposal = proposals.get_one(pid)

        print "{}tagging proposal {}{}{} with tag {}{}{}...".format(F.RESET,
                F.GREEN, u(proposal.title), F.RESET,
                F.GREEN, tag_name, F.RESET
        ),

        proposals.tag_proposal(pid, tag_name)
        affected += 1
        print F.GREEN + "OK"

    print F.RESET + "**********************************************************"
    print "{}{}{} proposals have been tagged with {}{}{}".format(
            F.GREEN, affected, F.RESET,
            F.GREEN, tag_name, F.RESET
    )

def put_tag_if_absent_of(new_tag, tag_names):
    service = ProposalService()
    wanted_tags = tag_names.split(",")
    operations = {"doing nothing": 0, "adding tag": 0}
    all_proposals = service.query()

    for proposal in all_proposals:
        has_wanted_tag = any([ proposal.tagged_as(tag) for tag in wanted_tags ])

        action = "doing nothing" if has_wanted_tag else "adding tag"
        print "{}proposal {}{}-{}{} has tags {}{}{}, and as such we are {}{}{}...".format(F.RESET,
                F.GREEN, proposal.id, u(proposal.title), F.RESET,
                F.GREEN, proposal.tag_names, F.RESET,
                F.GREEN, action, F.RESET
        ),
        operations[action] += 1

        if not has_wanted_tag:
            service.tag_proposal(proposal.id, new_tag)

        print F.GREEN + "OK"

    print F.RESET + "**********************************************************"
    print "{}{}{} proposals have been scanned".format(F.GREEN, len(all_proposals), F.RESET)
    print "{}tag {}{}{} has been added to {}{}{} proposals".format(F.RESET,
        F.GREEN, new_tag, F.RESET,
        F.GREEN, operations["adding tag"], F.RESET
    )
    print "{}the remaining {}{}{} already have some tag of {}{}{}, so we did nothing with them".format(F.RESET,
        F.GREEN, operations["doing nothing"], F.RESET,
        F.GREEN, tag_names, F.RESET
    )


