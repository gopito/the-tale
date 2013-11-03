# coding: utf-8

from the_tale.common.postponed_tasks import PostponedTaskPrototype


class AbilityPrototype(object):

    COST = None

    NAME = None
    DESCRIPTION = None

    @classmethod
    def get_type(cls): return cls.__name__.lower()

    def ui_info(self):
        return {'type': self.get_type()}

    def activate(self, hero, data):
        from the_tale.game.workers.environment import workers_environment
        from the_tale.game.abilities.postponed_tasks import UseAbilityTask

        data['hero_id'] = hero.id

        ability_task = UseAbilityTask(ability_type=self.get_type(),
                                      hero_id=hero.id,
                                      data=data)

        task = PostponedTaskPrototype.create(ability_task)

        workers_environment.supervisor.cmd_logic_task(hero.account_id, task.id)

        return task

    def use(self, *argv, **kwargs):
        raise NotImplementedError
