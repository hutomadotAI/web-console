import factory


class AiFactory(factory.Factory):

    aiid = '9cf6290f-7c23-40a8-a3e8-381dd9153f2a'
    client_token = 'eyJhbGciOiJIUzI1NiIsImNhbGciOiJERUYifQ.eNocyrsKwzAMheF30VyB5bu6lTaDwSRQunQqimO_QOhU8u4Rnc4P5_vBc6kTXP_zudcyza9lrm-4wK2Uhx7cRrRsBqZmHXojGcX1jC7TtjEFN6yo3r-r4tiHSatVQsaj56HViDGQtBTE504RjhMAAP__.m0ChIKk2E_tiNgTG5CHcTG5VHQjHoQSti6wP9XH-UPM'
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
