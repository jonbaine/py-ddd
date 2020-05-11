from app.application.persist_event import PersistEventCommand
from app.application.get_events import GetEventsQuery
from app.infrastructure.boot import Boot
from flask import Flask, jsonify, session
from uuid import uuid4
import logging


boot = Boot()
boot.start()
injector = boot.injector
app = Flask(__name__)


@app.route('/event')
def get_events():
    logging.debug('GET all events')
    handler = injector.get_service('app.application.query.get_events').instance
    result = handler.handle(GetEventsQuery())
    print(result)
    return jsonify(result)


@app.route('/event/<identifier>')
def get_event(identifier):
    logging.debug('GET event with ID')
    handler = injector.get_service('app.application.query.get_events').instance
    result = handler.handle(GetEventsQuery(identifier))
    return jsonify(result)


@app.route('/event', methods=['POST', 'PATCH'])
def post_event():
    logging.debug('POST new event')
    if session['name'] is None:
        logging.debug('POST failed: no name was attached')
        return jsonify({'response': 'failed', 'reason': 'no name was attached'})
    handler = injector.get_service(
        'app.application.command.persist_event'
    ).instance
    handler.instance.handle(
        PersistEventCommand(
            uuid4(),
            session['name']
        )
    )
    return jsonify({'response': 'done'})


