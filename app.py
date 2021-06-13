from flask import Flask, abort
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, reqparse, inputs, fields, marshal_with
import sys
from datetime import date

app = Flask(__name__)
db = SQLAlchemy(app)

# write your code here


api = Api(app)  # create an API object that accepts a flask application object as an argument:
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calendar.db'


resource_fields = {
    "id": fields.Integer,
    "event": fields.String,
    "date": fields.String
}

resource_fields_post = {
    "message": fields.String,
    "event": fields.String,
    "date": fields.String,
}

resource_fields_delete = {
    "message": fields.String
}


class Events(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)


class TodayResource(Resource):
    @marshal_with(resource_fields)
    def get(self):
        return Events.query.filter(Events.date == date.today().strftime("%Y-%m-%d")).all()


class PostResource(Resource):
    @marshal_with(resource_fields_post)
    def post(self):
        args = parser.parse_args()
        new_event = Events(event=args['event'], date=args['date'])
        db.session.add(new_event)
        db.session.commit()
        args.update({"date": args["date"].strftime("%Y-%m-%d")})
        return {"message": "The event has been added!", "event": args["event"],
                "date": args["date"]}


class GetResource(Resource):
    @marshal_with(resource_fields)
    def get(self):
        args = date_parser.parse_args()
        if args["start_time"] and args["end_time"]:
            events = Events.query.filter(
                Events.date <= args['end_time'].strftime("%Y-%m-%d"),
                Events.date >= args['start_time'].strftime("%Y-%m-%d")
            ).all()
            return events
        else:
            return Events.query.all()


class EventByID(Resource):
    @marshal_with(resource_fields)
    def get(self, event_id):
        event = Events.query.filter(Events.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        return event


class DeleteEventByID(Resource):
    @marshal_with(resource_fields_delete)
    def delete(self, event_id):
        event = Events.query.filter(Events.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        db.session.delete(event)
        db.session.commit()
        return {"message": "The event has been deleted!"}


api.add_resource(EventByID, '/event/<int:event_id>')
api.add_resource(DeleteEventByID, '/event/<int:event_id>')
api.add_resource(TodayResource, "/event/today")
api.add_resource(GetResource, "/event")
api.add_resource(PostResource, "/event")
parser = reqparse.RequestParser()
date_parser = reqparse.RequestParser()

parser.add_argument(
    "date",
    type=inputs.date,
    help="The event date with the correct format is required! The correct format is YYYY-MM-DD!",
    required=True

)

parser.add_argument(
    "event",
    type=str,
    help="The event name is required!",
    required=True
)

date_parser.add_argument(
    "start_time",
    type=inputs.date,
    help="The format is YYYY-MM-DD",
    required=False
)

date_parser.add_argument(
    "end_time",
    type=inputs.date,
    help="The format is YYYY-MM-DD",
    required=False
)


# do not change the way you run the program
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
