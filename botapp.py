import sys
import json
from flask import Flask, request
import telepot
import logging
import urlfetch

try:
    from Queue import Queue
except ImportError:
    from queue import Queue

"""
$ python2.7 webhook_flask_skeleton.py <token> <listening_port> <webhook_url>
Webhook path is '/abc' (see below), therefore:
<webhook_url>: https://<base>/abc
"""

def get_definition(term):
    url = 'https://mashape-community-urban-dictionary.p.mashape.com/define?term=' + term
    udheaders = {
        "X-Mashape-Key": UD_TOKEN,
        "Accept": "text/plain"
    }
    result = urlfetch.fetch(url=url, headers=udheaders)

    return json.loads(result.content)

def on_chat_message(msg):
    content_type, chat_type, chat_id, msg_date, msg_id = telepot.glance(msg, long=True)
    logging.info(msg)
    if (content_type == 'text'):
        resp = get_definition(msg['text'])
        if (resp['result_type'] != 'no_results'):
            definition = resp['list'][0]
            bot.sendMessage(chat_id, u'{}: {}{usage}'.format(definition['word'], definition['definition'], usage = "\r\n \r\nUsage: \r\n \r\n{}".format(definition['example']) if definition['example'] != '' else ""))
        else:
            bot.sendMessage(chat_id, u'No one says that')

def on_callback_query(msg):
    query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
    print 'Callback query:', query_id, from_id, data

# need `/setinline`
def on_inline_query(msg):
    query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
    print 'Inline Query:', query_id, from_id, query_string
    definitions = get_definition(query_string)

    # Compose your own answers
    articles = []
    for definition in definitions['list']:
        articles.append({'type': 'article',
                         'id': str(definition['defid']),
                         'title': definition['definition'],
                         'message_text': u'{}: {}{usage}'.format(definition['word'], definition['definition'], usage = "\r\n \r\nUsage: \r\n \r\n{}".format(definition['example']) if definition['example'] != '' else "")
                        })

    bot.answerInlineQuery(query_id, articles)

# need `/setinlinefeedback`
def on_chosen_inline_result(msg):
    result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
    print 'Chosen Inline Result:', result_id, from_id, query_string


TOKEN = "200808779:AAFd5_hX2wxdTfuOCAzsSYQTY0BhKbT8LR4"
UD_TOKEN = "8JL3NIJz9FmshRaXK5l8xa044FaEp1CDZtzjsnJ2Oqc10FJ83g"
URL = 'https://urbandictionarybot-tsangiotis.rhcloud.com/%s' % TOKEN

app = Flask(__name__)
bot = telepot.Bot(TOKEN)
update_queue = Queue()  # channel between `app` and `bot`

bot.message_loop({'chat': on_chat_message,
                  'callback_query': on_callback_query,
                  'inline_query': on_inline_query,
                  'chosen_inline_result': on_chosen_inline_result}, source=update_queue)  # take updates from queue

@app.route('/%s' % TOKEN, methods=['GET', 'POST'])
def pass_update():
    logging.info("hey there")
    update_queue.put(request.data)  # pass update to bot
    return 'OK %s' % bot.getMe()

if __name__ == '__main__':
    bot.setWebhook(URL)
    app.run(debug=True)
