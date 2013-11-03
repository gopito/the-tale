# coding: utf-8
import mock

from dext.utils import s11n

from textgen.words import Noun

from the_tale.common.utils import testcase

from the_tale.accounts.logic import register_user

from the_tale.game.logic import create_test_map

from the_tale.game.map.relations import TERRAIN
from the_tale.game.heroes.prototypes import HeroPrototype

from the_tale.game.artifacts.prototypes import ArtifactRecordPrototype
from the_tale.game.artifacts.models import ARTIFACT_RECORD_STATE
from the_tale.game.artifacts.relations import ARTIFACT_TYPE

from the_tale.game.mobs.storage import mobs_storage
from the_tale.game.mobs.relations import MOB_RECORD_STATE, MOB_TYPE
from the_tale.game.mobs.prototypes import MobPrototype, MobRecordPrototype
from the_tale.game.mobs.forms import ModerateMobRecordForm


class MobsPrototypeTests(testcase.TestCase):

    def setUp(self):
        super(MobsPrototypeTests, self).setUp()
        create_test_map()

        result, account_id, bundle_id = register_user('test_user')
        self.hero = HeroPrototype.get_by_account_id(account_id)

        mobs_storage.sync(force=True)

    def test_serialization(self):
        mob = mobs_storage.all()[0].create_mob(self.hero)
        self.assertEqual(mob, MobPrototype.deserialize(mob.serialize()))

    def test_deserialization_of_disabled_mob(self):
        mob_record = mobs_storage.all()[0]
        mob = mob_record.create_mob(self.hero)

        data = mob.serialize()

        mob_record.state = MOB_RECORD_STATE.DISABLED
        mob_record.save()

        mob_2 = MobPrototype.deserialize(data)

        self.assertNotEqual(mob.id, mob_2.id)


    def test_load_data(self):
        self.assertEqual(len(mobs_storage.all()), 3) # create_test_map create 3 random mobs
        self.assertFalse(mobs_storage.has_mob('wrong_id'))
        self.assertTrue(mobs_storage.has_mob('mob_1'))
        self.assertTrue(mobs_storage.has_mob('mob_2'))
        self.assertTrue(mobs_storage.has_mob('mob_3'))

    def test_storage_version_update_on_create(self):
        old_version = mobs_storage.version
        MobRecordPrototype.create_random(uuid='bandit', state=MOB_RECORD_STATE.DISABLED)
        self.assertNotEqual(old_version, mobs_storage.version)

    def test_storage_version_update_on_save(self):
        mob = MobRecordPrototype.create_random(uuid='bandit', state=MOB_RECORD_STATE.DISABLED)
        old_version = mobs_storage.version
        mob.save()
        self.assertNotEqual(old_version, mobs_storage.version)

    def test_mob_attributes(self):
        MobRecordPrototype.create(uuid='bandit',
                                  level=1,
                                  name='bandint',
                                  description='bandint',
                                  abilities=['hit', 'thick', 'slow', 'extra_strong'],
                                  terrains=TERRAIN._ALL,
                                  type=MOB_TYPE.CIVILIZED,
                                  state=MOB_RECORD_STATE.ENABLED)
        mobs_storage.sync(force=True)

        bandit = MobPrototype(record=mobs_storage.get_by_uuid('bandit'), level=1)

        self.assertEqual(bandit.health_cooficient, 1.025)
        self.assertEqual(bandit.initiative, 0.975)
        self.assertEqual(bandit.damage_modifier, 1.05)

    def test_get_loot(self):

        self.hero._model.level = 5

        mob_record = MobRecordPrototype.create_random(uuid='bandit', level=2, state=MOB_RECORD_STATE.ENABLED)
        mob = MobPrototype(record=mob_record, level=3)
        artifact_1 = ArtifactRecordPrototype.create_random('bandit_loot', mob=mob_record, type_=ARTIFACT_TYPE.USELESS, state=ARTIFACT_RECORD_STATE.ENABLED)
        artifact_2 = ArtifactRecordPrototype.create_random('bandit_artifact', mob=mob_record, type_=ARTIFACT_TYPE.HELMET, state=ARTIFACT_RECORD_STATE.ENABLED)

        with mock.patch('the_tale.game.balance.formulas.artifacts_per_battle', lambda lvl: 1):
            artifact = mob.get_loot()
            self.assertEqual(artifact.level, mob.level)
            self.assertFalse(artifact.type._is_USELESS)
            self.assertEqual(artifact_2.id, artifact.record.id)

        with mock.patch('the_tale.game.balance.formulas.artifacts_per_battle', lambda lvl: 0),  mock.patch('the_tale.game.balance.constants.GET_LOOT_PROBABILITY', 1):
            artifact = mob.get_loot()
            self.assertEqual(artifact.level, mob.record.level)
            self.assertTrue(artifact.type._is_USELESS)
            self.assertEqual(artifact_1.id, artifact.record.id)

    def test_change_uuid(self):
        mob = MobRecordPrototype.create_random(uuid='bandit', state=MOB_RECORD_STATE.DISABLED)

        form = ModerateMobRecordForm({'name_forms': s11n.to_json(Noun.fast_construct('artifact name').serialize()),
                                      'uuid': 'new_uid',
                                      'level': '667',
                                      'terrains': [TERRAIN.PLANE_JUNGLE, TERRAIN.HILLS_JUNGLE],
                                      'approved': True,
                                      'type': MOB_TYPE.CIVILIZED,
                                      'abilities': ['hit', 'speedup'],
                                      'description': 'new description'})
        self.assertTrue(form.is_valid())
        self.assertEqual(mob.uuid, mobs_storage.get_by_uuid(mob.uuid).uuid)

        mob.update_by_moderator(form)

        self.assertEqual(mob.uuid, 'new_uid')
        self.assertEqual(mob.uuid, mobs_storage.get_by_uuid(mob.uuid).uuid)
