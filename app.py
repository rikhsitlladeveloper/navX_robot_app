import json
import os
import glob
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from pydantic import ValidationError
from werkzeug.utils import secure_filename
from launcher import Launcher, LaunchState
from validator import ValidateMapping, ValidateNavigation, ValidateUserRegister, ValidateUserDelete, RespWrapper
from utils import check_file_ex, get_ext_maps, compress_maps, extract_map
from utils import amr_robot_maps, slam_methods
from models import db, User, Role
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
CORS(app)
app.config.from_object('config.DevConfig')
db.init_app(app)
auth = HTTPBasicAuth()


@auth.get_user_roles
def get_user_roles(username):
    user = User.query.filter_by(username=username).first()
    role = [role.name for role in user.role]
    return role


@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user is not None and user.check_password(password):
        return user.username


@app.route('/')
@auth.login_required
def home():
    response = RespWrapper()
    response.data = {'launcher': Launcher.state.value}
    return jsonify(response.dict()), 200


@app.before_request
def before_first_request():
    compress_maps()


@app.route('/api/user/register', methods=['POST'])
@auth.login_required(role='admin')
def user_register():
    response = RespWrapper()
    req = request.get_json(silent=True)
    try:
        content = ValidateUserRegister.parse_raw(json.dumps(req))
        if content.username and content.password:
            if User.query.filter_by(username=content.username).first():
                response.error = True
                response.data = {'username': content.username}
                response.message = 'user already exists'
                return jsonify(response.dict()), 200
            user_role = Role.query.filter_by(name=content.role).first()
            new_user = User(username=content.username, role=[user_role])
            new_user.set_password(content.password)
            db.session.add(new_user)
            db.session.commit()
            response.message = 'new user added'
            response.data = {'username': new_user.username}
            return jsonify(response.dict()), 201
    except ValidationError as e:
        response.error = True
        response.message = 'wrong request'
        response.data = {'validation error': e.json()}
        return jsonify(response.dict()), 400


@app.route('/api/user/delete', methods=['DELETE'])
@auth.login_required(role='admin')
def delete_user():
    response = RespWrapper()
    req = request.get_json(silent=True)
    # TODO check if not user to delete is current user
    try:
        content = ValidateUserDelete.parse_raw(json.dumps(req))
        if not content.username == auth.current_user():
            user = User.query.filter_by(username=content.username).first()
            if user is not None:
                db.session.delete(user)
                db.session.commit()
                response.message = 'deleted user'
            else:
                response.message = 'no such user'
            response.data = {'username': content.username}
            return jsonify(response.dict()), 200
        else:
            response.error = True
            response.message = f'{auth.current_user()} can not delete {content.username}'
            return jsonify(response.dict()), 200
    except ValidationError as e:
        response.error = True
        response.message = 'wrong request'
        response.data = {'validation error': e.json()}
        return jsonify(response.dict()), 400


@app.route('/api/bringup/start', methods=['POST'])
@auth.login_required
def bringup():
    response = RespWrapper()
    response.data = {'launcher': Launcher.state.value}
    # response.headers.add('Access-Control-Allow-Origin', '*')
    if Launcher.state == LaunchState.OFF:
        Launcher.start_bringup()
        response.data = {'launcher': Launcher.state.value,
                         'pid': Launcher.bringup_pid(),
                         'state': Launcher.bringup_state().value}
        return jsonify(response.dict()), 200
    return jsonify(response.dict()), 200


@app.route('/api/bringup/stop', methods=['POST'])
@auth.login_required
def stopbringup():
    if Launcher.state == LaunchState.MAPPING:
        Launcher.stop_mapping()
        Launcher.stop_bringup()

    elif Launcher.state == LaunchState.NAVIGATION:
        Launcher.stop_navigation()
        Launcher.stop_bringup()

    elif Launcher.state == LaunchState.BRINGUP:
        Launcher.stop_bringup()
    response = RespWrapper()
    response.data = {'launcher': Launcher.state.value}
    # response.headers.add('Access-Control-Allow-Origin', '*')
    return jsonify(response.dict()), 200


@app.route('/api/mapping/start', methods=['POST'])
@auth.login_required(role='admin')
def startmapping():
    response = RespWrapper()
    req = request.get_json(silent=True)
    if Launcher.state == LaunchState.OFF:
        response.error = True
        response.message = "first launch bringup on '/api/bringup/start'"
        response.data = {'launcher': Launcher.state.value}
        return jsonify(response.dict()), 400

    elif Launcher.state == LaunchState.NAVIGATION:
        response.error = True
        response.message = "first stop navigation on '/api/navigation/stop'"
        response.data = {'launcher': Launcher.state.value}
        return jsonify(response.dict()), 400

    elif Launcher.state == LaunchState.MAPPING:
        response.error = True
        response.message = "mapping is running you should stop current mapping on '/api/mapping/stop'"
        response.data = {'launcher': Launcher.state.value}
        return jsonify(response.dict()), 400
    try:
        content = ValidateMapping.parse_raw(json.dumps(req))
        if content.slam_method in slam_methods:
            Launcher.start_mapping(content.slam_method)
        else:
            response.error = True
            response.message = "wrong slam method"
            response.data = {'slam_methods': slam_methods, 'launcher': Launcher.state.value}
            return jsonify(response.dict()), 400
    except ValidationError as e:
        response.error = True
        response.message = 'wrong request'
        response.data = {'validation error': (e.json())}
        return jsonify(response.dict()), 400
    response.data = {'launcher': Launcher.state.value,
                     'pid': Launcher.mapping_pid(),
                     'state': Launcher.mapping_state().value}
    return jsonify(response.dict()), 200


@app.route('/api/mapping/stop', methods=['POST'])
@auth.login_required(role='admin')
def stopmapping():
    response = RespWrapper()
    if Launcher.state == LaunchState.MAPPING:
        Launcher.stop_mapping()
    response.data = {'launcher': Launcher.state.value}
    return jsonify(response.dict()), 200


@app.route('/api/mapping/savemap', methods=['POST'])
@auth.login_required(role='admin')
def savemap():
    req = request.get_json(silent=True)
    response = RespWrapper()
    if Launcher.state == LaunchState.MAPPING:
        try:
            content = ValidateNavigation.parse_raw(json.dumps(req))
            existing_maps = [ext_map[0] for ext_map in get_ext_maps()]
            if content.map_name in existing_maps:
                response.error = True
                response.message = f"map with name {content.map_name} already exists"
                return jsonify(response.dict()), 400
            os.system("ros2 run nav2_map_server map_saver_cli -f" + " " + amr_robot_maps + content.map_name)
            os.system(
                "convert" + " " + amr_robot_maps + content.map_name + ".pgm" + " " + amr_robot_maps
                + content.map_name + ".png")
            compress_maps()

        except ValidationError as e:
            response.error = True
            response.message = 'wrong request'
            response.data = {'validation error': e.json()}
            return jsonify(response.dict()), 400
        response.message = f"map saved in {amr_robot_maps + content.map_name}"
        response.data = {'launcher': Launcher.state.value}
        return jsonify(response.dict()), 200

    else:
        response.error = True
        response.message = "first launch mapping on '/api/mapping/start'"
        response.data = {'launcher': Launcher.state.value}
        return jsonify(response.dict()), 400


@app.route('/api/mapping/getmap', methods=['POST'])
@auth.login_required(role='admin')
def upload_map():
    response = RespWrapper()
    req = request.get_json(silent=True)
    try:
        content = ValidateNavigation.parse_raw(json.dumps(req))
        existing_maps = [ext_map[0] for ext_map in get_ext_maps()]
        if check_file_ex(content.map_name, 'zip', amr_robot_maps) and content.map_name in existing_maps:
            return send_from_directory(amr_robot_maps, f"{content.map_name}.zip")
        else:
            response.error = True
            response.message = f"map_file '{content.map_name}' doesn't exists"
            response.data = {'existing_maps': existing_maps}
            return jsonify(response.dict())

    except ValidationError as e:
        response.error = True
        response.message = 'wrong request'
        response.data = {'validation error': e.json()}
        return jsonify(response.dict()), 400


@app.route('/api/mapping/loadmap', methods=['POST'])
@auth.login_required(role='admin')
def downloadmap():
    response = RespWrapper()
    if 'map_file' not in list(request.files.keys()):
        response.error = True
        response.message = "key 'map_file' doesn't exist"
        return jsonify(response.dict()), 400
    map_file = request.files['map_file']
    if map_file:
        if map_file.content_type in ('application/zip', 'application/zip-compressed',
                                     'application/x-zip-compressed', 'application/x-zip'):
            map_path = os.path.join(os.path.join(amr_robot_maps, secure_filename(map_file.filename)))
            # TODO check duplicates
            map_file.save(map_path)
            extract_map(map_path)
            response.message = f'map files saved in {map_path}'
            return jsonify(response.dict())
        else:
            response.error = True
            response.message = "'map_file' mimetype must be 'application/zip'"
            return jsonify(response.dict()), 400
    else:
        response.error = True
        response.message = "'map_file' empty"
        return jsonify(response.dict()), 400


@app.route('/api/mapping/delete', methods=['DELETE'])
@auth.login_required(role='admin')
def delete_map():
    response = RespWrapper()
    req = request.get_json(silent=True)
    try:
        content = ValidateNavigation.parse_raw(json.dumps(req))
        existing_maps = [ext_map[0] for ext_map in get_ext_maps()]
        if content.map_name in existing_maps:
            files = glob.glob(amr_robot_maps + f"{content.map_name}.*")
            for file in files:
                os.remove(file)
            response.message = f"map {content.map_name} deleted"
            return jsonify(response.dict()), 200
        else:
            response.error = True
            response.message = f"map_file '{content.map_name}' doesn't exists"
            response.data = {'existing_maps': existing_maps}
            return jsonify(response.dict())

    except ValidationError as e:
        response.error = True
        response.message = 'wrong request'
        response.data = {'validation error': e.json()}
        return jsonify(response.dict()), 400


@app.route('/api/navigation/start', methods=['POST'])
@auth.login_required
def startnavigation():
    response = RespWrapper()
    req = request.get_json(silent=True)
    if Launcher.state == LaunchState.OFF:
        response.error = True
        response.message = "first launch bringup on '/api/bringup/start'"
        response.data = {'launcher': Launcher.state.value}
        return jsonify(response.dict()), 400

    elif Launcher.state == LaunchState.NAVIGATION:
        response.error = True
        response.message = "first stop current navigation on '/api/navigation/stop'"
        response.data = {'launcher': Launcher.state.value}
        return jsonify(response.dict()), 400

    elif Launcher.state == LaunchState.MAPPING:
        response.error = True
        response.message = "first stop mapping on '/api/mapping/stop'"
        response.data = {'launcher': Launcher.state.value}
        return jsonify(response.dict()), 400

    try:
        content = ValidateNavigation.parse_raw(json.dumps(req))
        existing_maps = [ext_map[0] for ext_map in get_ext_maps()]
        if content.map_name in existing_maps:
            if content.with_virtual_walls:
                if f"{content.map_name}_virtual" in existing_maps:
                    Launcher.start_navigation(content.map_name, content.local_planner_type, content.with_virtual_walls)
                else:
                    Launcher.start_navigation(content.map_name, content.local_planner_type)
                    response.message = f"virtual_map '{content.map_name}_virtual' doesn't exists"
                response.data = {'launcher': Launcher.state.value,
                                 'pid': Launcher.navigation_pid(),
                                 'state': Launcher.navigation_state().value}
                return jsonify(response.dict()), 200
            else:
                Launcher.start_navigation(content.map_name, content.local_planner_type)
                response.data = {'launcher': Launcher.state.value,
                                 'pid': Launcher.navigation_pid(),
                                 'state': Launcher.navigation_state().value}
                return jsonify(response.dict()), 200

        else:
            response.error = True
            response.message = f"map_file '{content.map_name}' doesn't exists"
            response.data = {'existing_maps': existing_maps}
            return jsonify(response.dict())

    except ValidationError as e:
        response.error = True
        response.message = 'wrong request'
        response.data = {'validation error': e.json()}
        return jsonify(response.dict()), 400


@app.route('/api/navigation/stop', methods=['POST'])
@auth.login_required
def stopnavigation():
    response = RespWrapper()
    if Launcher.state == LaunchState.NAVIGATION:
        Launcher.stop_navigation()
    response.data = {'launcher': Launcher.state.value}
    return jsonify(response.dict()), 200


@app.route('/api/bringup/state', methods=['GET'])
@auth.login_required
def bringup_state():
    response = RespWrapper()
    state = Launcher.bringup_state().value
    response.data = {'launcher': Launcher.state.value,
                     'pid': Launcher.bringup_pid(),
                     'state': state}
    return jsonify(response.dict()), 200


@app.route('/api/navigation/state', methods=['GET'])
@auth.login_required
def navigation_state():
    response = RespWrapper()
    state = Launcher.navigation_state().value
    response.data = {'launcher': Launcher.state.value,
                     'pid': Launcher.navigation_pid(),
                     'state': state}
    return jsonify(response.dict()), 200


@app.route('/api/mapping/state', methods=['GET'])
@auth.login_required
def mapping_state():
    response = RespWrapper()
    state = Launcher.mapping_state().value
    response.data = {'launcher': Launcher.state.value,
                     'pid': Launcher.mapping_pid(),
                     'state': state}
    return jsonify(response.dict()), 200


@app.route('/api/robot/reboot', methods=['GET'])
@auth.login_required(role='admin')
def reboot():
    response = RespWrapper()
    os.system('sudo reboot now')
    response.message = 'rebooting robot'
    return jsonify(response.dict()), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
