# coding: utf-8
import mock

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user
from the_tale.game.heroes.prototypes import HeroPrototype
from the_tale.game.logic_storage import LogicStorage

from the_tale.game.heroes.logic import create_mob_for_hero
from the_tale.game.logic import create_test_map
from the_tale.game.actions.prototypes import ActionBattlePvE1x1Prototype
from the_tale.game.prototypes import TimePrototype

class BattlePvE1x1ActionTest(testcase.TestCase):

    def setUp(self):
        super(BattlePvE1x1ActionTest, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)
        self.action_idl = self.hero.actions.current_action

        self.action_battle = ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=create_mob_for_hero(self.hero))

    def tearDown(self):
        pass


    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_battle.leader, True)
        self.assertEqual(self.action_battle.bundle_id, self.action_idl.bundle_id)
        self.storage._test_save()

    @mock.patch('the_tale.game.actions.prototypes.battle.make_turn', lambda a, b, c: None)
    def test_mob_killed(self):
        self.assertEqual(self.hero.statistics.pve_kills, 0)
        self.action_battle.mob.health = 0
        self.storage.process_turn(second_step_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)
        self.assertEqual(self.hero.statistics.pve_kills, 1)
        self.storage._test_save()


    @mock.patch('the_tale.game.balance.formulas.artifacts_per_battle', lambda lvl: 0)
    @mock.patch('the_tale.game.balance.constants.GET_LOOT_PROBABILITY', 1)
    @mock.patch('the_tale.game.actions.prototypes.battle.make_turn', lambda a, b, c: None)
    def test_loot(self):
        self.assertEqual(self.hero.statistics.loot_had, 0)
        self.assertEqual(len(self.hero.bag.items()), 0)
        self.action_battle.mob.health = 0
        self.storage.process_turn()
        self.assertEqual(self.hero.statistics.loot_had, 1)
        self.assertEqual(len(self.hero.bag.items()), 1)
        self.storage._test_save()

    @mock.patch('the_tale.game.balance.formulas.artifacts_per_battle', lambda lvl: 1)
    @mock.patch('the_tale.game.actions.prototypes.battle.make_turn', lambda a, b, c: None)
    def test_artifacts(self):
        self.assertEqual(self.hero.statistics.artifacts_had, 0)
        self.assertEqual(len(self.hero.bag.items()), 0)
        self.action_battle.mob.health = 0
        self.storage.process_turn()
        self.assertEqual(self.hero.statistics.artifacts_had, 1)
        self.assertEqual(len(self.hero.bag.items()), 1)
        self.storage._test_save()

    @mock.patch('the_tale.game.actions.prototypes.battle.make_turn', lambda a, b, c: None)
    def test_hero_killed(self):
        self.assertEqual(self.hero.statistics.pve_deaths, 0)
        self.hero.health = 0
        self.storage.process_turn(second_step_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)
        self.assertTrue(not self.hero.is_alive)
        self.assertEqual(self.hero.statistics.pve_deaths, 1)
        self.storage._test_save()

    def test_full_battle(self):

        current_time = TimePrototype.get_current_time()

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn()
            current_time.increment_turn()

        self.assertTrue(self.action_idl.leader)

        self.storage._test_save()

    def test_bit_mob(self):
        old_mob_health = self.action_battle.mob.health
        old_action_percents = self.action_battle.percents

        self.action_battle.bit_mob(0.33)

        self.assertTrue(self.action_battle.mob.health < old_mob_health)
        self.assertTrue(self.action_battle.percents > old_action_percents)
        self.assertTrue(self.action_battle.updated)

    def test_bit_mob_and_kill(self):

        self.action_battle.bit_mob(1)

        self.assertEqual(self.action_battle.mob.health, 0)
        self.assertEqual(self.action_battle.percents, 1)
        self.assertTrue(self.action_battle.updated)
