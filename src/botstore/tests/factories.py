import factory


class DeveloperFactory(factory.Factory):

    devid = 'd14b441b-e2a2-4b9f-be9b-4301647e1265'
    company = 'Hu:toma'
    website = 'http://www.hutoma.com'
    name = 'Hutoma'
    email = 'support@hutoma.com'
    country = 'United Kingdom'


class MetadataFactory(factory.Factory):

    name = 'Chit-Chat'
    description = 'Free Chit-Chat bot'
    longDescription = 'Just include this bot in your AI to get instant chit-chat'
    alertMessage = ''
    badge = ''
    price = 0
    sample = 'Hi\nWhat\'s your name?\nWhat is MY name?'
    category = 'Entertainment'
    licenseType = 'Free'
    lastUpdate = '2017-07-12T10:06:00.000Z'
    privacyPolicy = 'https://www.hutoma.com/privacy.pdf'
    classification = 'EVERYONE'
    version = '1.0'
    videoLink = ''
    botIcon = '_chat.png'
    dev_id = 'd14b441b-e2a2-4b9f-be9b-4301647e1265'
    publishingState = 'PUBLISHED'
    aiid = 'e1bb8226-e8ce-467a-8305-bc2fcb89dd7f'
    botId = 1


class BotDetailsFactory(factory.Factory):

    owned = False
    order = factory.Sequence(lambda n: n)
    developer = factory.build(dict, FACTORY_CLASS=DeveloperFactory)
    metadata = factory.build(dict, FACTORY_CLASS=MetadataFactory)
