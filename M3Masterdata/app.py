from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import sqlobject

app = Flask(__name__)
api = Api(app)

DATABASE_URI = 'sqlite:m3.db'
connection = sqlobject.connectionForURI(DATABASE_URI)
sqlobject.sqlhub.processConnection = connection
     
class SensorNode(sqlobject.SQLObject):
    node_id = sqlobject.StringCol(unique=True)
    name = sqlobject.StringCol(unique=True)
    rootpath = sqlobject.StringCol(unique=True)
    # sensors?

SensorNode.createTable(ifNotExists=True)

'''
class SensorNodeSensor(sqlobject.SQLObject):
    node_id = sqlobject.StringCol() # FK to parent
    sensor_index = sqlobject.IntCol() # unique with node_id
    name = sqlobject.StringCol()
    subpath = sqlobject.StringCol()
    sensor_type = sqlobject.EnumCol()

SensorNodeSensor.createTable(ifNotExists=True)
'''

class SensorNodeController(Resource):
    def get(self, node_id):
        try:
            node = SensorNode.select(SensorNode.q.node_id==node_id).getOne()
            return { 'node_id' : node.node_id, 'rootpath' : node.rootpath}
        except sqlobject.main.SQLObjectNotFound:
            abort(404, message="Sensor with id={} does not exists".format(node_id))

    def delete(self, node_id):
        try:
            node = SensorNode.select(SensorNode.q.node_id==node_id).getOne()
            SensorNode.delete(node.id)
            return 204
        except sqlobject.main.SQLObjectNotFound:
            abort(404, message="Sensor with id={} does not exists".format(node_id))

    def put(self, node_id):
        parser = reqparse.RequestParser()
        parser.add_argument('rootpath', required=True, nullable=False)
        args = parser.parse_args()

        try:
            node = SensorNode.select(SensorNode.q.node_id==node_id).getOne()
            node.rootpath = args['rootpath']
            return 201
        except sqlobject.main.SQLObjectNotFound:
            abort(404, message="Sensor with id={} does not exists".format(node_id))

class SensorNodeListeController(Resource):
    def get(self):
        selected_rows = SensorNode.select().orderBy(SensorNode.q.rootpath)
        
        nodes = []
        for node in selected_rows:
            nodes.append({
                'node_id' : node.node_id,
                'rootpath' : node.rootpath})
        
        return nodes 

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('rootpath', required=True, nullable=False)
        parser.add_argument('node_id', required=True, nullable=False)
        args = parser.parse_args()
        try:
            node = SensorNode(node_id=args['node_id'], rootpath=args['rootpath'])
            return { 'node_id' : node.node_id, 'rootpath' : node.rootpath}
        except sqlobject.dberrors.DuplicateEntryError:
            abort(400, message="Sensor with id={} or path={} already exists".format(args['node_id'], args['rootpath']))

api.add_resource(SensorNodeListeController, '/nodes/sensors')
api.add_resource(SensorNodeController, '/nodes/<node_id>')

if __name__ == '__main__':
    app.run(debug=True)