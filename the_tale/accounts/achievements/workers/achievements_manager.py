# coding: utf-8

import Queue

from django.utils.log import getLogger

from dext.settings import settings

from the_tale.common.amqp_queues import connection, BaseWorker

from the_tale.accounts.achievements.prototypes import GiveAchievementTaskPrototype, AccountAchievementsPrototype
from the_tale.accounts.achievements.storage import achievements_storage


class Worker(BaseWorker):

    logger = getLogger('the-tale.workers.achievements_achievements_manager')
    name = 'achievements manager'
    command_name = 'achievements_achievements_manager'

    def __init__(self, messages_queue, stop_queue):
        super(Worker, self).__init__(command_queue=messages_queue)
        self.stop_queue = connection.SimpleQueue(stop_queue)
        self.initialized = True

    def clean_queues(self):
        super(Worker, self).clean_queues()
        self.stop_queue.queue.purge()

    def initialize(self):
        self.logger.info('ACHIEVEMENT_MANAGER INITIALIZED')

    def run(self):

        while not self.exception_raised and not self.stop_required:
            try:
                cmd = self.command_queue.get(block=True, timeout=10)
                cmd.ack()

                settings.refresh()
                self.process_cmd(cmd.payload)
            except Queue.Empty:
                self.logger.info('try to update commands')
                settings.refresh()
                self.add_achievements()

    def add_achievements(self):
        for task in GiveAchievementTaskPrototype.from_query(GiveAchievementTaskPrototype._db_all()):

            achievements = AccountAchievementsPrototype.get_by_account_id(task.account_id)
            achievements.achievements.add_achievement(achievements_storage[task.achievement_id])
            achievements.save()

            task.remove()

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.initialized = False
        self.stop_required = True
        self.stop_queue.put({'code': 'stopped', 'worker': 'achievements_manager'}, serializer='json', compression=None)
        self.logger.info('ACHIEVEMENTS MANAGER STOPPED')
