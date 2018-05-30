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
    handover_reset_timeout_seconds = 0
    error_threshold_handover = -1
    handover_message = 'Some default response'


class AIDetails(factory.Factory):

    training_file = ''
    intents = []
    skills = []


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


class EntityFactory(factory.Factory):
    entity_name = 'sys.places'
    entity_values = 'Value 1\x9DValue 2\x9DValue 3'


class EntityFormsetFactory(factory.Factory):
    entity_name = 'sys.places'
    required = True
    n_prompts = 3
    prompts = 'User prompt 1\x9DUser prompt 2\x9DUser prompt 3'
    label = 'entity_label'


class IntentFactory(factory.Factory):
    intent_name = 'Intent_name'
    responses = 'Response 1\x9DResponse 2\x9DResponse 3'
    user_says = 'User say 1\x9DUser say 2\x9DUser say 3'
    variables = []
    webhook = ''


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
