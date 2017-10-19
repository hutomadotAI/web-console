import factory


class EntityFactory(factory.Factory):
    name = "entity_name"
    values = ["value a", "value b", "value c", "value d"]


class EntitiesFactory(factory.Factory):
    entities = [
        {"name": "entity_name", "values": ["value_a", "value_b", "value_c", "value_d"]},
        {"name": "entity_name_2", "values": ["value_e", "value_f", "value_g"]}
    ]
