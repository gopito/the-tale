# coding: utf-8

from dext.utils.urls import url

from common.utils import testcase
from common.utils.permissions import sync_group

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user, login_url


from game.logic import create_test_map


from achievements.prototypes import SectionPrototype, KitPrototype, RewardPrototype


class BaseRequestTests(testcase.TestCase):

    def setUp(self):
        super(BaseRequestTests, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')
        self.account_1 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.account_2 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_3', 'test_user_3@test.com', '111111')
        self.account_3 = AccountPrototype.get_by_id(account_id)

        group_edit = sync_group('edit kit', ['achievements.edit_kit'])
        group_moderate = sync_group('moderate kit', ['achievements.moderate_kit'])

        group_edit.account_set.add(self.account_2._model)
        group_moderate.account_set.add(self.account_3._model)

        self.section_1 = SectionPrototype.create(caption=u'section_1', description=u'description_1')
        self.section_2 = SectionPrototype.create(caption=u'section_2', description=u'description_2')

        self.kit_1 = KitPrototype.create(section=self.section_1, caption=u'kit_1', description=u'description_1')
        self.kit_2 = KitPrototype.create(section=self.section_1, caption=u'kit_2', description=u'description_2')

        self.reward_1_1 = RewardPrototype.create(kit=self.kit_1, caption=u'reward_1_1', text=u'text_1_1')
        self.reward_1_2 = RewardPrototype.create(kit=self.kit_1, caption=u'reward_1_2', text=u'text_1_2')



class KitsIndexTests(BaseRequestTests):

    def setUp(self):
        super(KitsIndexTests, self).setUp()
        self.index_url = url('achievements:kits:')

    def test_success(self):
        texts = [('pgf-no-kits-message', 0),
                 ('pgf-no-kits-message', 0)]
        texts.extend((kit.caption, 1) for kit in KitPrototype._db_all())
        texts.extend((kit.caption, 1) for kit in KitPrototype._db_all())

        self.check_html_ok(self.request_html(self.index_url), texts=texts)

    def test_no_kits(self):
        KitPrototype._db_all().delete()
        KitPrototype._db_all().delete()
        self.check_html_ok(self.request_html(self.index_url),
                           texts=(('pgf-no-kits-message', 1),
                                  ('pgf-no-kits-message', 0)))

    def test_no_kits_in_kit(self):
        KitPrototype._db_all().delete()
        self.check_html_ok(self.request_html(self.index_url),
                           texts=(('pgf-no-kits-message', 0),
                                  ('pgf-no-kits-message', 2)))


class KitsNewTests(BaseRequestTests):

    def setUp(self):
        super(KitsNewTests, self).setUp()
        self.new_url = url('achievements:kits:new')

    def test_login_required(self):
        self.check_redirect(self.new_url, login_url(self.new_url))

    def test_edit_rights_required(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.new_url),
                           texts=(('achievements.kits.no_edit_rights', 1)))

    def test_success(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.new_url),
                           texts=(('achievements.kits.no_edit_rights', 0)))


class KitsCreateTests(BaseRequestTests):

    def setUp(self):
        super(KitsCreateTests, self).setUp()
        self.create_url = url('achievements:kits:create')

    def get_post_data(self):
        return {'section': self.section_1.id,
                'caption': 'caption_3',
                'description': 'description_3'}

    def test_login_required(self):
        self.check_ajax_error(self.post_ajax_json(self.create_url, self.get_post_data()),
                              'common.login_required')
        self.assertEqual(KitPrototype._db_all().count(), 2)

    def test_edit_rights_required(self):
        self.request_login(self.account_1.email)
        self.check_ajax_error(self.post_ajax_json(self.create_url, self.get_post_data()),
                              'achievements.kits.no_edit_rights')
        self.assertEqual(KitPrototype._db_all().count(), 2)

    def test_form_errors(self):
        self.request_login(self.account_2.email)
        self.check_ajax_error(self.post_ajax_json(self.create_url, {}),
                              'achievements.kits.form_errors')
        self.assertEqual(KitPrototype._db_all().count(), 2)

    def test_success(self):
        self.request_login(self.account_2.email)
        self.check_ajax_ok(self.post_ajax_json(self.create_url, {}))
        self.assertEqual(KitPrototype._db_all().count(), 3)

        kit = KitPrototype._db_get_object(2)

        self.assertFalse(kit.approved)
        self.assertEqual(kit.section_id, self.section_1.id)
        self.assertEqual(kit.caption, 'caption_3')
        self.assertEqual(kit.description, 'description_3')


class KitsShowTests(BaseRequestTests):

    def setUp(self):
        super(KitsShowTests, self).setUp()
        self.show_url = url('achievements:kits:show', self.kit_1.id)

    def test_success(self):
        self.check_html_ok(self.request_html(self.show_url),
                           texts=[self.section_1.caption,
                                  (self.section_2.caption, 0),
                                  self.kit_1.caption,
                                  (self.kit_2.caption, 0),
                                  (self.reward_1_1.caption, 1),
                                  (self.reward_1_2.caption, 1),
                                  ('pgf-no-rewards-message', 0)])

    def test_no_rewards_in_section(self):
        RewardPrototype._db_all().delete()
        self.check_html_ok(self.request_html(self.show_url),
                           texts=[self.section_1.caption,
                                  (self.section_2.caption, 0),
                                  (self.kit_1.caption, 1),
                                  (self.kit_2.caption, 0),
                                  (self.reward_1_1.caption, 0),
                                  (self.reward_1_2.caption, 0),
                                  ('pgf-no-rewards-message', 1)])


class KitsEditTests(BaseRequestTests):

    def setUp(self):
        super(KitsEditTests, self).setUp()
        self.show_url = url('achievements:kits:edit', self.kit_1.id)

    def test_login_required(self):
        self.check_redirect(self.show_url, login_url(self.show_url))

    def test_edit_rights_required(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.show_url),
                           texts=(('achievements.kits.no_edit_rights', 1)))


    def test_moderate_rights_required(self):
        KitPrototype._db_all().update(approved=True)

        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.show_url),
                           texts=(('achievements.kits.no_moderate_rights', 1)))

    def test_success__for_edit(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.show_url),
                           texts=[self.kit_1.caption,
                                  self.kit_1.description])

    def test_success__for_moderate(self):
        KitPrototype._db_all().update(approved=True)

        self.request_login(self.account_3.email)
        self.check_html_ok(self.request_html(self.show_url),
                           texts=[self.kit_1.description,
                                  self.kit_1.caption])


class KitsUpdateTests(BaseRequestTests):

    def setUp(self):
        super(KitsEditTests, self).setUp()
        self.update_url = url('achievements:kits:update', self.kit_1.id)

    def get_post_data(self):
        return {'caption': 'caption_edited',
                'description': 'description_edited',
                'section': self.section_2.id}

    def test_login_required(self):
        self.check_ajax_error(self.post_ajax_json(self.update_url, self.get_post_data()), 'common.login_required')

    def test_edit_rights_required(self):
        self.request_login(self.account_1.email)
        self.check_ajax_error(self.post_ajax_json(self.update_url, self.get_post_data()),
                              'achievements.kits.no_edit_rights')

        self.kit_1.reload()
        self.assertEqual(self.kit_1.caption, 'caption')
        self.assertEqual(self.kit_1.description, 'description')
        self.assertEqual(self.kit_1.section_id, self.section_1.id)


    def test_moderate_rights_required(self):
        KitPrototype._db_all().update(approved=True)

        self.request_login(self.account_2.email)
        self.check_ajax_error(self.post_ajax_json(self.update_url, self.get_post_data()),
                              'achievements.kits.no_moderate_rights')

        self.kit_1.reload()
        self.assertEqual(self.kit_1.caption, 'caption')
        self.assertEqual(self.kit_1.description, 'description')
        self.assertEqual(self.kit_1.section_id, self.section_1.id)

    def test_form_errors(self):
        self.request_login(self.account_2.email)
        self.check_ajax_error(self.post_ajax_json(self.update_url, {}),
                              'achievements.kits.update.forms_error')

        self.kit_1.reload()
        self.assertEqual(self.kit_1.caption, 'caption')
        self.assertEqual(self.kit_1.description, 'description')
        self.assertEqual(self.kit_1.section_id, self.section_1.id)

    def test_success__for_edit(self):
        self.request_login(self.account_2.email)
        self.check_ajax_ok(self.post_ajax_json(self.update_url))

        self.kit_1.reload()
        self.assertEqual(self.kit_1.caption, 'caption_edited')
        self.assertEqual(self.kit_1.description, 'description_edited')
        self.assertEqual(self.kit_1.section_id, self.section_2.id)

    def test_success__for_moderate(self):
        KitPrototype._db_all().update(approved=True)

        self.request_login(self.account_3.email)
        self.check_ajax_ok(self.post_ajax_json(self.update_url))

        self.kit_1.reload()
        self.assertEqual(self.kit_1.caption, 'caption_edited')
        self.assertEqual(self.kit_1.description, 'description_edited')
        self.assertEqual(self.kit_1.section_id, self.section_2.id)



class KitsApproveTests(BaseRequestTests):

    def setUp(self):
        super(KitsApproveTests, self).setUp()
        self.approve_url = url('achievements:kits:approve', self.kit_1.id)

    def test_login_required(self):
        self.check_ajax_error(self.post_ajax_json(self.approve_url), 'common.login_required')

    def test_moderate_rights_required(self):
        self.request_login(self.account_2.email)
        self.check_ajax_error(self.post_ajax_json(self.approve_url), 'achievements.kits.no_moderate_rights')

    def test_success(self):
        self.request_login(self.account_3.email)
        self.assertFalse(self.kit_1.approved)
        self.check_ajax_ok(self.post_ajax_json(self.approve_url))
        self.kit_1.reload()
        self.assertTrue(self.kit_1.approved)



class KitsDisapproveTests(BaseRequestTests):

    def setUp(self):
        super(KitsDisapproveTests, self).setUp()
        self.disapprove_url = url('achievements:kits:disapprove', self.kit_1.id)

    def test_login_required(self):
        self.check_ajax_error(self.post_ajax_json(self.disapprove_url), 'common.login_required')

    def test_moderate_rights_required(self):
        self.request_login(self.account_2.email)
        self.check_ajax_error(self.post_ajax_json(self.disapprove_url), 'achievements.kits.no_moderate_rights')

    def test_success(self):
        KitPrototype._db_all().update(approved=True)
        self.kit_1.reload()

        self.request_login(self.account_3.email)

        self.assertTrue(self.kit_1.approved)
        self.check_ajax_ok(self.post_ajax_json(self.disapprove_url))
        self.kit_1.reload()
        self.assertFalse(self.kit_1.approved)
