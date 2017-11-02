import factory


class AiFactory(factory.Factory):

    aiid = '9cf6290f-7c23-40a8-a3e8-381dd9153f2a'
    client_token = 'token'
    name = 'Testy'
    description = ''
    created_on = '2017-08-22T13:30:22.000Z'
    is_private = False
    personality = 0
    confidence = 0.4000000059604645
    voice = 1
    language = 'en-US'
    timezone = 'Europe/London'
    ai_status = 'ai_undefined'
    phase_1_progress = 1
    phase_2_progress = 0
    deep_learning_error = 0
    training_file_uploaded = True
    publishing_state = 'NOT_PUBLISHED'
    default_chat_responses = [
        'Erm...What?'
    ]
    linked_bots = [
        1
    ]


class AIImportJSON(factory.Factory):
    name = 'Foo IIss4'
    description = ''
    isPrivate = False
    personality = 0
    confidence = 0.4
    voice = 1
    language = 'en_US'
    timezone = 'Europe/London'
    intents = []
    trainingFile = 'Some content'
    entities = []
    version = 1


class UnauthorizedFactory(factory.Factory):
    status = {
        'code': 401,
        'info': 'Requires authentication'
    }


class NameExistsFactory(factory.Factory):
    status = {
        'code': 400,
        'info': 'A bot with that name already exists'
    }


class SuccessFactory(factory.Factory):
    status = {
        'code': 201,
        'info': 'OK'
    }

class EntityFactory(factory.Factory):
    name = "entity_name"
    values = ["value a", "value b", "value c", "value d"]


class EntitiesFactory(factory.Factory):
    entities = [
        {"sys.any": "entity_name", "values": ["value_a", "value_b", "value_c", "value_d"], "is_system":True},
        {"name": "entity_name_2", "values": ["value_e", "value_f", "value_g"], "is_system":False}
    ]