# coding: utf-8

from django.db import models

from common.utils.enum import create_enum

PHRASE_CANDIDATE_STATE = create_enum('PHRASE_CANDIDATE_STATE', ( ('IN_QUEUE', 0, u'ожидает проверку'),
                                                                 ('REMOVED', 1, u'удалена'),
                                                                 ('APPROVED', 2, u'одобрена'),
                                                                 ('ADDED', 3, u'добавлена') ) )


class PhraseCandidate(models.Model):

    MAX_TEXT_LENGTH = 1024*10

    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now_add=True, null=False)

    author = models.ForeignKey('accounts.Account', null=False, related_name='+')
    moderator = models.ForeignKey('accounts.Account', null=True, related_name='+')

    text = models.TextField(null=False, blank=True, max_length=MAX_TEXT_LENGTH)

    type = models.CharField(null=False, blank=False, max_length=256)
    type_name = models.CharField(null=False, blank=False, max_length=256, default=u'')

    subtype = models.CharField(null=False, blank=False, max_length=256, default=u'')
    subtype_name = models.CharField(null=False, blank=False, max_length=256, default=u'')

    state = models.IntegerField(null=False, default=PHRASE_CANDIDATE_STATE.IN_QUEUE, choices=PHRASE_CANDIDATE_STATE.CHOICES, db_index=True)

    class Meta:
        permissions = (("moderate_phrase_candidate", u"Может редактировать фразы-кандидаты"), ) # game designer
        permissions = (("add_phrase_candidate_to_game", u"Может добавлять фразы-кандидаты"), ) # developer
