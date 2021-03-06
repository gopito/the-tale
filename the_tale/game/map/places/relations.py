# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from questgen.relations import PLACE_TYPE as QUEST_PLACE_TYPE

from the_tale.game.balance import constants as c

from the_tale.game.map.places import technical_words

class BUILDING_STATE(DjangoEnum):
    records = ( ('WORKING', 0, u'работает'),
                ('DESTROYED', 1, u'уничтожено') )

class CITY_PARAMETERS(DjangoEnum):
    records = ( ('PRODUCTION', 0, u'Производство'),
                ('SAFETY', 1, u'Безопасность'),
                ('FREEDOM', 2, u'Свободы'),
                ('TRANSPORT', 3, u'Транспорт'),
                ('TAX', 4, u'Пошлина'))


class BUILDING_TYPE(DjangoEnum):
    records = ( ('SMITHY', 0, u'кузница'),
                ('FISHING_LODGE', 1, u'домик рыболова'),
                ('TAILOR_SHOP', 2, u'мастерская портного'),
                ('SAWMILL', 3, u'лесопилка'),
                ('HUNTER_HOUSE', 4, u'домик охотника'),
                ('WATCHTOWER', 5, u'сторожевая башня'),
                ('TRADING_POST', 6, u'торговый пост'),
                ('INN', 7, u'трактир'),
                ('DEN_OF_THIEVE', 8, u'логово вора'),
                ('FARM', 9, u'ферма'),
                ('MINE', 10, u'шахта'),
                ('TEMPLE', 11, u'храм'),
                ('HOSPITAL', 12, u'больница'),
                ('LABORATORY', 13, u'лаборатория'),
                ('SCAFFOLD', 14, u'плаха'),
                ('MAGE_TOWER', 15, u'башня мага'),
                ('GUILDHALL', 16, u'ратуша'),
                ('BUREAU', 17, u'бюро'),
                ('MANOR', 18, u'поместье'),
                ('SCENE', 19, u'сцена'),
                ('MEWS', 20, u'конюшни'),
                ('RANCH', 21, u'ранчо') )



class RESOURCE_EXCHANGE_TYPE(DjangoEnum):
    parameter = Column(unique=False, primary=False, single_type=False)
    amount = Column(unique=False, primary=False, single_type=False)
    direction = Column(unique=False, primary=False)

    PRODUCTION_BASE = int(c.PLACE_GOODS_BONUS / 2)
    SAFETY_BASE = c.PLACE_SAFETY_FROM_BEST_PERSON / 10.0
    TRANSPORT_BASE = c.PLACE_TRANSPORT_FROM_BEST_PERSON / 10.0
    TAX_BASE = 0.025

    records = ( ('NONE',  0, u'ничего', None, 0, 0),

                ('PRODUCTION_SMALL',  1, u'%d продукции' % PRODUCTION_BASE, CITY_PARAMETERS.PRODUCTION, PRODUCTION_BASE, 1),
                ('PRODUCTION_NORMAL', 2, u'%d продукции' % (PRODUCTION_BASE * 2), CITY_PARAMETERS.PRODUCTION, PRODUCTION_BASE * 2, 1),
                ('PRODUCTION_LARGE',  3, u'%d продукции' % (PRODUCTION_BASE * 4), CITY_PARAMETERS.PRODUCTION, PRODUCTION_BASE * 4, 1),

                ('SAFETY_SMALL',      4, u'%.1f%% безопасности' % float(SAFETY_BASE * 100), CITY_PARAMETERS.SAFETY, SAFETY_BASE, 1),
                ('SAFETY_NORMAL',     5, u'%.1f%% безопасности' % float(SAFETY_BASE * 2 * 100), CITY_PARAMETERS.SAFETY, SAFETY_BASE * 2, 1),
                ('SAFETY_LARGE',      6, u'%.1f%% безопасности' % float(SAFETY_BASE * 4 * 100), CITY_PARAMETERS.SAFETY, SAFETY_BASE * 4, 1),

                ('TRANSPORT_SMALL',   7, u'%.1f%% транспорта' % float(TRANSPORT_BASE * 100), CITY_PARAMETERS.TRANSPORT, TRANSPORT_BASE, 1),
                ('TRANSPORT_NORMAL',  8, u'%.1f%% транспорта' % float(TRANSPORT_BASE * 2 * 100), CITY_PARAMETERS.TRANSPORT, TRANSPORT_BASE * 2, 1),
                ('TRANSPORT_LARGE',   9, u'%.1f%% транспорта' % float(TRANSPORT_BASE * 4 * 100), CITY_PARAMETERS.TRANSPORT, TRANSPORT_BASE * 4, 1),

                ('TAX_SMALL',   10, u'%.1f%% пошлины' % float(TAX_BASE * 100), CITY_PARAMETERS.TAX, TAX_BASE, -1),
                ('TAX_NORMAL',  11, u'%.1f%% пошлины' % float(TAX_BASE * 2 * 100), CITY_PARAMETERS.TAX, TAX_BASE * 2, -1),
                ('TAX_LARGE',   12, u'%.1f%% пошлины' % float(TAX_BASE * 4 * 100), CITY_PARAMETERS.TAX, TAX_BASE * 4, -1) )


def _modifier_linguistics_restrictions(modifier):
    def _linguistics_restrictions():
        from the_tale.linguistics.relations import TEMPLATE_RESTRICTION_GROUP
        from the_tale.linguistics.storage import restrictions_storage
        return (restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.CITY_MODIFIER, CITY_MODIFIERS.index_name[modifier].value).id, )
    return _linguistics_restrictions


class CITY_MODIFIERS(DjangoEnum):
    quest_type = Column(unique=False)
    utg_name_form = Column()
    linguistics_restrictions = Column()
    description = Column()

    records = ( ('TRADE_CENTER', 0, u'Торговый центр', QUEST_PLACE_TYPE.NONE,
                 technical_words.MODIFIER_TRADE_CENTER, _modifier_linguistics_restrictions('TRADE_CENTER'),
                 u'В городе идёт оживлённая торговля, поэтому герои всегда могут найти выгодную цену для продажи своих трофеев или покупки артефактов. Увеличивается производство и уровень свободы в городе.'),
                ('CRAFT_CENTER', 1, u'Город мастеров', QUEST_PLACE_TYPE.NONE,
                 technical_words.MODIFIER_CRAFT_CENTER, _modifier_linguistics_restrictions('CRAFT_CENTER'),
                 u'Большое количество мастеров, трудящихся в городе, позволяет героям приобретать лучшие артефакты. Увеличивается уровень производства в городе.'),
                ('FORT', 2, u'Форт', QUEST_PLACE_TYPE.NONE,
                 technical_words.MODIFIER_FORT, _modifier_linguistics_restrictions('FORT'),
                 u'Постоянное присутствие военных делает окрестности города безопаснее для путешествий.'),
                ('POLITICAL_CENTER', 3, u'Политический центр', QUEST_PLACE_TYPE.NONE,
                 technical_words.MODIFIER_POLITICAL_CENTER, _modifier_linguistics_restrictions('POLITICAL_CENTER'),
                 u'Активная политическая жизнь приводит к тому, что в городе увеличивается уровень свободы. Также увеличивается радиус влияния города и ускоряется восстановление стабильности.'),
                ('POLIC', 4, u'Полис', QUEST_PLACE_TYPE.NONE,
                 technical_words.MODIFIER_POLIC, _modifier_linguistics_restrictions('POLIC'),
                 u'Самостоятельная политика города вместе с большими свободами граждан способствуют увеличению размера экономики и уровня свободы в городе. Кроме того увеличивается радиус, в котором город влияет на изменение ландшафта.'),
                ('RESORT', 5, u'Курорт', QUEST_PLACE_TYPE.NONE,
                 technical_words.MODIFIER_RESORT, _modifier_linguistics_restrictions('RESORT'),
                 u'Город прославлен своими здравницами и особой атмосферой, в которой раны затягиваются особенно быстро. При посещении города герои полностью восстанавливают своё здоровье, их спутники также восстанавливают немного здоровья. Увеличивается уровень безопасности города и уровень свободы.'),
                ('TRANSPORT_NODE', 6, u'Транспортный узел', QUEST_PLACE_TYPE.NONE,
                 technical_words.MODIFIER_TRANSPORT_NODE, _modifier_linguistics_restrictions('TRANSPORT_NODE'),
                 u'Хорошие дороги и обилие гостиниц делают путешествие по дорогам в окрестностях города быстрым и комфортным. Увеличивается уровень транспорта в городе.'),
                ('OUTLAWS', 7, u'Вольница', QUEST_PLACE_TYPE.NONE,
                 technical_words.MODIFIER_OUTLAWS, _modifier_linguistics_restrictions('OUTLAWS'),
                 u'Город облюбован всевозможными авантюристами, бунтарями, беглыми преступниками, бастардами и просто свободолюбивыми людьми, которые готовы любыми средствами защищать свою свободу и свой уклад. Любое задание, связанное с этим городом, принесёт дополнительные опыт герою. Также в городе увеличен уровень свободы и уменьшен уровень безопасности.'),
                ('HOLY_CITY', 8, u'Святой город', QUEST_PLACE_TYPE.HOLY_CITY,
                 technical_words.MODIFIER_HOLY_CITY, _modifier_linguistics_restrictions('HOLY_CITY'),
                 u'Город является средоточием религиозной жизни Пандоры. У каждого героя рано или поздно появляется желание посетить это святое место, чтобы дать отдых своему духу. Обилие паломников способствует развитию транспортной системы города, но излишняя религиозность жителей отрицательно сказывается на производстве и свободе. Сильная энергетика города позволяет Хранителям восстанавливать немного энергии, когда их герои посещают город.') )


class EFFECT_SOURCES(DjangoEnum):
    records = ( ('PERSON', 0, u'житель'),)
