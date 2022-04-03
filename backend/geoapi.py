# -*- coding: utf-8 -*-
# !/usr/bin/python

# Copyright (C) 2019 strangebit

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Dmitriy Kuptsov"
__copyright__ = "Copyright 2020, stangebit"
__license__ = "GPL"
__version__ = "0.0.1a"
__maintainer__ = "Dmitriy Kuptsov"
__email__ = "dmitriy.kuptsov@gmail.com"
__status__ = "development"

# Map ratio
# https://gis.stackexchange.com/questions/7430/what-ratio-scales-do-google-maps-zoom-levels-correspond-to

from flask import Flask
from flask import request, jsonify, send_from_directory
from flask import json, Response
from flask import g
# from flask_cors import CORS
from logging.config import dictConfig
from clustering import KMeansClustering
from UTMConverter import UTMConverter
import numpy as np
import decimal
import MySQLdb
import hashlib
import random
import datetime
import os
import re
import urllib2
from flask import Response
from math import sqrt
from math import pow
import sys
import json
from math import log
import base64
import atexit
import traceback
from weasyprint import HTML, CSS
from math import pi, sin, cos, asin, atan2
import smtplib
from config import config
import geopy
from geopy.distance import VincentyDistance
from tokens import Token
from utils import Utils
import tempfile
import codecs
import imgkit

app = Flask(__name__);
# CORS(app);

# This is too large but anyways 
random.seed(os.urandom(64));


def toRad(angle_deg):
    return (pi * angle_deg) / 180.0;


def toDeg(angle_rad):
    return 180.0 * angle_rad / pi;


def findLatLongFromPointAndDistance(coord, bearing, distance):
    origin = geopy.Point(coord[0], coord[1])
    destination = VincentyDistance(kilometers=distance / 1000).destination(origin, bearing);
    return [destination.latitude, destination.longitude]


# This will impact the performance of the system greatly
# but it was noticed that deadlocks can occur and so locking was introduced 
def lock_tables(cursor, tables, lock_type):
    query = "LOCK TABLES ";
    for table in tables:
        query += "%s %s," % (table, lock_type);
    query = query.rstrip(",");
    cursor.execute(query);


def unlock_tables(cursor):
    query = "UNLOCK TABLES";
    cursor.execute(query);


def connect_to_database():
    return MySQLdb.connect(host=config["DB_HOST"],
                           user=config["DB_USER"],
                           passwd=config["DB_PASSWORD"],
                           db=config["DB"],
                           charset="utf8");


@app.before_request
def db_connect():
    g.db = connect_to_database();
    g.cur = g.db.cursor(MySQLdb.cursors.DictCursor);


@app.teardown_request
def db_disconnect(exception=None):
    unlock_tables(g.cur);
    g.db.close();


def exit_handler():
    db = connect_to_database();
    cur = db.cursor(MySQLdb.cursors.DictCursor);
    unlock_tables(cur);
    db.close();


atexit.register(exit_handler);


def register_authorization_failure(resource, token):
    try:
        token_hash = Token.get_token_hash(token);
        lock_tables(g.cur, ["authorization_failures"], "WRITE");
        query = "INSERT INTO geomap.authorization_failures(token, resource, access_time) VALUES(%s, %s, NOW());"
        g.cur.execute(query, [token_hash, resource]);
        g.db.commit();
    except Exception as e:
        pass
    finally:
        unlock_tables(g.cur)


def register_authentication_failure(username, password):
    MAX_USERNAME_LENGTH = 100;
    MAX_PASSWORD_LENGTH = 100;
    if len(username) > MAX_USERNAME_LENGTH:
        username = username[:MAX_USERNAME_LENGTH];
    if len(password) > MAX_PASSWORD_LENGTH:
        password = password[:MAX_PASSWORD_LENGTH];
    try:
        lock_tables(g.cur, ["authentication_failures"], "WRITE");
        query = "INSERT INTO geomap.authentication_failures(username, password, access_time) VALUES(%s, SHA2(%s, 256), NOW())";
        g.cur.execute(query, [username, password + config["PASSWORD_SALT"]]);
        g.db.commit();
    except Exception as e:
        pass
    finally:
        unlock_tables(g.cur)


@app.route("/api/load_map_library/")
def load_map_library():
    source = urllib2.urlopen(config["GOOGLE_MAPS_API_URL"]);
    data = source.read();
    return Response(data, mimetype="text/javascript; charset=UTF-8");


def query_stats(resource, delta):
    histogram_sample_size = 1000;
    try:
        lock_tables(g.cur, ["query_stats", "query_histogram"], "WRITE");
        print "LOCKING TABLES query_stats, query_histogram"
        query = "SELECT sum_x_squared, mean_time, max_time, min_time, std, sample_size FROM geomap.query_stats WHERE resource = %s";
        g.cur.execute(query, [resource]);
        rows = g.cur.fetchall();
        if len(rows) > 0:
            sum_x_squared = rows[0]["sum_x_squared"] + pow(delta, 2);
            mean_time = rows[0]["mean_time"];
            max_time = rows[0]["max_time"];
            min_time = rows[0]["min_time"];
            std = rows[0]["std"];
            sample_size = rows[0]["sample_size"];
            sample_size = sample_size + 1;
        else:
            sum_x_squared = pow(delta, 2);
            mean_time = 0
            max_time = 0
            min_time = sys.maxint
            std = 0
            sample_size = 1
            query = "INSERT INTO geomap.query_stats(sum_x_squared, mean_time, max_time, min_time, std, sample_size, resource) VALUES(%s, %s, %s, %s, %s, %s, %s)";
            g.cur.execute(query, [sum_x_squared, mean_time, max_time, min_time, std, sample_size, resource]);
            g.db.commit();
        if max_time < delta:
            max_time = delta;
        if min_time > delta:
            min_time = delta;
        mean_time = ((sample_size - 1) * mean_time + delta) / sample_size;
        std = sqrt(sum_x_squared / sample_size - pow(mean_time, 2));
        query = "UPDATE geomap.query_stats SET sum_x_squared = %s, mean_time = %s, max_time = %s, min_time = %s, std = %s, sample_size = %s WHERE resource = %s";
        g.cur.execute(query, [sum_x_squared, mean_time, max_time, min_time, std, sample_size, resource]);
        g.db.commit();
        query = "SELECT MIN(id) AS min_id FROM (SELECT id FROM geomap.query_histogram WHERE resource = %s ORDER BY id DESC LIMIT %s) AS dt;"
        g.cur.execute(query, [resource, histogram_sample_size]);
        row = g.cur.fetchone();
        min_id = row["min_id"];
        query = "DELETE FROM geomap.query_histogram WHERE id < %s AND resource = %s;"
        g.cur.execute(query, [min_id, resource]);
        g.cur.fetchall();
        g.db.commit();
        query = "INSERT INTO geomap.query_histogram(resource, duration) VALUES(%s, %s)";
        g.cur.execute(query, [resource, delta]);
        g.db.commit();
    except Exception as e:
        print e
    finally:
        print "UNLOCKING TABLES query_stats, query_histogram"
        unlock_tables(g.cur);


def ip_based_authorization(remote_ip):
    if remote_ip in ["192.168.0.213", "127.0.0.1", "192.168.0.2"]:
        return True
    return False


def get_role_for_token(token, remote_ip):
    role_id = Token.get_role_id(token)
    if not role_id:
        query = "SELECT id FROM roles WHERE role = %s";
        g.cur.execute(query, ["guest"]);
        row = g.cur.fetchone();
        return row["id"];
    else:
        return role_id


def get_user_id_for_token(token, remote_ip):
    return Token.get_user_id(token);


def authorize(resource, token, access_right, remote_ip, remote_port):
    role_id = get_role_for_token(token, remote_ip);
    query = "SELECT p.role_id, r.access_right FROM geomap.permissions p INNER JOIN geomap.rights r ON p.access_right_id = r.id INNER JOIN geomap.resources rs ON rs.id = p.resource_id WHERE p.role_id = %s AND rs.name = %s AND r.access_right = %s";
    g.cur.execute(query, [role_id, resource, access_right]);
    rows = g.cur.fetchall();
    if len(rows) != 1:
        return False;
    else:
        return True;


@app.route("/api/histogram/")
def histogram():
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if not ip_based_authorization(remote_ip):
        return jsonify({"status": "failure", "reason": "forbidden"});
    if authorize("/api/histogram/", token, "read", remote_ip, remote_port) != True:
        register_authorization_failure("/api/histogram/", token);
        return jsonify({"status": "failure", "reason": "forbidden"});
    query = "SELECT * FROM geomap.query_histogram";
    g.cur.execute(query);
    rows = g.cur.fetchall();
    result = dict();
    for row in rows:
        if row["resource"] not in result.keys():
            result[row["resource"]] = [];
        result[row["resource"]].append(row["duration"]);
    return jsonify({
        "status": "success",
        "data": result
    });


@app.route("/api/stats/")
def stats():
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if not ip_based_authorization(remote_ip):
        return jsonify({"status": "failure", "reason": "forbidden"});
    if authorize("/api/stats/", token, "read", remote_ip, remote_port) != True:
        register_authorization_failure("/api/stats/", token);
        return jsonify({"status": "failure", "reason": "forbidden"});
    query = "SELECT resource, mean_time, max_time, min_time, sum_x_squared, std, sample_size FROM geomap.query_stats";
    g.cur.execute(query);
    rows = g.cur.fetchall();
    result = [];
    for row in rows:
        result.append({
            "resource": row["resource"],
            "mean_time": row["mean_time"],
            "max_time": row["max_time"],
            "min_time": row["min_time"],
            "sum_x_squared": row["sum_x_squared"],
            "std": row["std"],
            "sample_size": row["sample_size"]
        });
    return jsonify({
        "status": "success",
        "data": result
    });


@app.route("/api/get_pending_registrations/")
def get_pending_registrations():
    start_time = datetime.datetime.now();
    # token = request.args.get("token") or "";
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if not ip_based_authorization(remote_ip):
        return jsonify({"status": "failure", "reason": "forbidden"});
    if authorize("/api/get_pending_registrations/", token, "read", remote_ip, remote_port) != True:
        register_authorization_failure("/api/get_pending_registrations/", token);
        return jsonify({"status": "failure", "reason": "forbidden"});
    query = "SELECT id, user_first_name, user_last_name, phone_number, email_address, description FROM geomap.pending_registrations";
    g.cur.execute(query);
    rows = g.cur.fetchall();
    result = dict();
    for row in rows:
        result[row["id"]] = {
            "first_name": row["user_first_name"],
            "last_name": row["user_last_name"],
            "phone_number": row["phone_number"],
            "email_address": row["email_address"],
            "description": row["description"],
        }
    end_time = datetime.datetime.now();
    query_stats("/api/get_pending_registrations/", (end_time - start_time).total_seconds());
    return jsonify({
        "status": "success",
        "data": result
    });


@app.route("/api/delete_pending_registration/")
def delete_pending_registration():
    start_time = datetime.datetime.now();
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    pending_registration_id = request.args.get("pending_registration_id") or "";
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if not ip_based_authorization(remote_ip):
        return jsonify({"status": "failure", "reason": "forbidden"});
    if authorize("/api/delete_pending_registration/", token, "delete", remote_ip, remote_port) != True:
        register_authorization_failure("/api/delete_pending_registration/", token);
        return jsonify({"status": "failure", "reason": "forbidden"});
    if not re.match("^[1-9]{1}[0-9]*$", pending_registration_id):
        return jsonify({
            "status": "failure",
            "reason": "Неверный идентификатор"
        });
    query = "SELECT * FROM geomap.pending_registrations WHERE id = %s";
    g.cur.execute(query, [pending_registration_id]);
    row = g.cur.fetchone();
    if not row:
        return jsonify({
            "status": "failure",
            "reason": "Неверный идентификатор"
        });
    try:
        print "LOCKING TABLES pending_registrations";
        lock_tables(g.cur, ["pending_registrations"], "WRITE")
        query = "DELETE FROM geomap.pending_registrations WHERE id = %s";
        g.cur.execute(query, [pending_registration_id]);
        g.db.commit();
    except:
        return jsonify({
            "status": "failure",
            "reason": "Внутренняя ошибка сервера"
        });
    finally:
        print "UNLOCKING TABLES pending_registrations";
        unlock_tables(g.cur);
    end_time = datetime.datetime.now();
    query_stats("/api/delete_pending_registration/", (end_time - start_time).total_seconds());
    return jsonify({
        "status": "success"
    });


@app.route("/api/request_registration/", methods=["POST"])
def request_registration():
    start_time = datetime.datetime.now();
    try:
        data = json.loads(request.stream.read());
    except:
        return Utils.make_response({
            "status": "failure",
            "reason": "Ошибка при декодировании JSON объекта"
        }, 200);
    first_name = data.get("first_name") or "";
    last_name = data.get("last_name") or "";
    phone_number = data.get("phone_number") or "";
    email_address = data.get("email_address") or "";
    description = data.get("description") or "";
    if not re.match(ur"^[a-z\u0430-\u044f]{1,99}$", first_name, re.IGNORECASE | re.UNICODE):
        return jsonify({
            "status": "failure",
            "reason": "Неверное имя"
        });
    if not re.match(ur"^[a-z\u0430-\u044f]{1,99}$", last_name, re.IGNORECASE | re.UNICODE):
        return jsonify({
            "status": "failure",
            "reason": "Неверная фамилия"
        });
    if not re.match("^[a-zA-Z0-9._-]+@[a-zA-Z]+\.[a-zA-Z]{2,4}$", email_address):
        return jsonify({
            "status": "failure",
            "reason": "Неверный адрес электронной почты"
        });
    if not re.match("^\+[0-9]{3}-?[0-9]{2,3}-?[0-9]{5,7}$", phone_number):
        return jsonify({
            "status": "failure",
            "reason": "Неверный номер телефона"
        });
    if not re.match(ur"^[\u0430-\u044f\s0-9.,\sa-z]{1,1000}$", description, re.IGNORECASE | re.UNICODE):
        return jsonify({
            "status": "failure",
            "reason": "Неверное описание"
        });
    query = "SELECT * FROM geomap.pending_registrations WHERE email_address = %s OR phone_number = %s";
    g.cur.execute(query, [email_address, phone_number])
    rows = g.cur.fetchall();
    if len(rows) > 0:
        return jsonify({
            "status": "failure",
            "reason": "Пользователь с таким адресом или телефоном уже существует"
        });
    query = "SELECT * FROM geomap.users WHERE email_address = %s OR phone_number = %s";
    g.cur.execute(query, [email_address, phone_number])
    rows = g.cur.fetchall();
    if len(rows) > 0:
        return jsonify({
            "status": "failure",
            "reason": "Пользователь с таким адресом или телефоном уже существует"
        });
    try:
        print "LOCKING TABLES pending_registrations";
        lock_tables(g.cur, ["pending_registrations"], "WRITE")
        query = "INSERT INTO geomap.pending_registrations(user_first_name, user_last_name, phone_number, email_address, description) VALUES(%s, %s, %s, %s, %s)";
        g.cur.execute(query, [first_name, last_name, phone_number, email_address, description]);
        g.db.commit();
    except Exception as e:
        return jsonify({
            "status": "failure",
            "reason": "Внутренняя ошибка сервера"
        });
    finally:
        print "UNLOCKING TABLES pending_registrations";
        unlock_tables(g.cur);
    if config["NOTIFY_NEW_REGISTRATION_BY_EMAIL"]:
        try:
            server = smtplib.SMTP(config["SMTP_SERVER"], config["SMTP_PORT"]);
            server.login(config["SMTP_USERNAME"], config["SMTP_PASSWORD"]);
            msg = "Получено новый запрос на регистрацию пользователя. Пожалуйста, посетите страницу для администратора";
            server.sendmail(config["FROM_EMAIL"], config["TO_EMAIL"], msg);
        except Exception as e:
            print e
    end_time = datetime.datetime.now()
    query_stats("/api/request_registration/", (end_time - start_time).total_seconds());
    return jsonify({
        "status": "success",
        "reason": "Запрос принят. Ждите ответа администратора."
    });


@app.route("/api/authenticate/", methods=["POST"])
def authenticate():
    start_time = datetime.datetime.now();
    try:
        data = json.loads(request.stream.read());
    except:
        return Utils.make_response({
            "status": "failure",
            "reason": "Ошибка при декодировании JSON объекта"
        }, 200);
    username = data.get("username") or "";
    password = data.get("password") or "";
    if not re.match("^[a-z0-9]{4,100}$", username):
        return jsonify({
            "status": "failure",
            "reason": "Неверное имя пользователя"
        });
    if not re.match("^(?=.*[A-Z]+)(?=.*[a-z]+)(?=.*[0-9]+)(?=.*[$#%]+)", password) or not re.match(
            "^[a-zA-Z0-9#$%&@]{10,100}$", password):
        return jsonify({
            "status": "failure",
            "reason": "Неверный пароль"
        });
    # sha256 = hashlib.new("sha256");
    # random_token = "".join([random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ") for c in range(32)]);
    # sha256.update(random_token);
    # Hash based token is redundant information since we have IV already
    # token_hash = sha256.hexdigest();
    random_token = Utils.token_hex();
    query = "SELECT u.id AS user_id, u.role_id, r.role FROM users u INNER JOIN roles r ON r.id = u.role_id WHERE u.username = %s AND u.password = SHA2((%s), 256) AND enabled = TRUE;";
    g.cur.execute(query, [username, password + config["PASSWORD_SALT"]]);
    row = g.cur.fetchone();
    print(g.cur._last_executed);
    if not row:
        register_authentication_failure(username, password);
        return Utils.make_response({
            "status": "failure",
            "reason": "Неверное имя пользователя или пароль"
        }, 200);
    role_id = row["role_id"];
    user_id = row["user_id"];
    role = row["role"];

    expire_date = datetime.datetime.utcnow() + datetime.timedelta(seconds=config["MAX_SESSION_DURATION_IN_SECONDS"])
    end_time = datetime.datetime.now();
    query_stats("/api/authenticate/", (end_time - start_time).total_seconds());
    response = jsonify({
        "status": "success",
        "role": role
    });
    response.set_cookie(
        "token",
        Token.encode(
            role_id,
            user_id,
            random_token,
            config["SERVER_NONCE"],
            config["MAX_SESSION_DURATION_IN_SECONDS"]),
        secure=False,
        httponly=True,
        expires=expire_date,
        samesite="Strict");
    return response


@app.route("/api/logout/")
def logout():
    start_time = datetime.datetime.now();
    end_time = datetime.datetime.now();
    query_stats("/api/logout/", (end_time - start_time).total_seconds());
    response = Utils.make_response({
        "status": "success"
    }, 200);
    response.set_cookie("token", "", expires=0)
    return response


@app.route("/api/check_token/")
def check_token():
    start_time = datetime.datetime.now();
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    end_time = datetime.datetime.now();
    query_stats("/api/check_token/", (end_time - start_time).total_seconds());
    return Utils.make_response({
        "status": "success",
        "authenticated": (True if token else False)
    }, 200);


@app.route("/api/get_role/")
def get_role():
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    role_id = get_role_for_token(token, None)
    role = "guest";
    if role_id:
        query = "SELECT role FROM roles WHERE id = %s";
        g.cur.execute(query, [role_id]);
        row = g.cur.fetchone();
        role = row["role"];
    return Utils.make_response({
        "status": "success",
        "authenticated": (True if token else False),
        "role": role
    }, 200);


@app.route("/api/get_roles/")
def get_roles():
    start_time = datetime.datetime.now();
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if not ip_based_authorization(remote_ip):
        return jsonify({"status": "failure", "reason": "forbidden"});
    if authorize("/api/get_roles/", token, "read", remote_ip, remote_port) != True:
        register_authorization_failure("/api/get_roles/", token);
        return jsonify({"status": "failure", "reason": "forbidden"});
    query = "SELECT id, role FROM geomap.roles";
    g.cur.execute(query);
    rows = g.cur.fetchall();
    result = dict();
    for row in rows:
        result[row["id"]] = row["role"];
    end_time = datetime.datetime.now();
    query_stats("/api/get_roles/", (end_time - start_time).total_seconds());
    return jsonify({
        "status": "success",
        "data": result
    });


@app.route("/api/add_user/", methods=["POST"])
def add_user():
    start_time = datetime.datetime.now();
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    try:
        data = json.loads(request.stream.read());
    except:
        return Utils.make_response({
            "status": "failure",
            "reason": "Ошибка при декодировании JSON объекта"
        }, 200);
    username = data.get("username") or "";
    password = data.get("password") or "";
    first_name = data.get("first_name") or "";
    last_name = data.get("last_name") or "";
    phone_number = data.get("phone_number") or "";
    email_address = data.get("email_address") or "";
    new_user_role_id = data.get("role_id") or "";
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if not ip_based_authorization(remote_ip):
        return jsonify({"status": "failure", "reason": "forbidden"});
    if authorize("/api/add_user/", token, "write", remote_ip, remote_port) != True:
        register_authorization_failure("/api/add_user/", token);
        return jsonify({"status": "failure", "reason": "forbidden"});
    if not re.match("^[a-z0-9]{5,100}$", username):
        return jsonify({
            "status": "failure",
            "reason": "Неверное имя пользователя"
        });
    if not re.match("^(?=.*[A-Z]+)(?=.*[a-z]+)(?=.*[0-9]+)(?=.*[$#%]+)", password) or not re.match(
            "^[a-zA-Z0-9#$%&@]{10,100}$", password):
        return jsonify({
            "status": "failure",
            "reason": "Неверный пароль"
        });
    if first_name != "" and not re.match("^[A-Z]{1}[a-z]{1,99}$", first_name):
        return jsonify({
            "status": "failure",
            "reason": "Неверное имя"
        });
    if last_name != "" and not re.match("^[A-Z]{1}[a-z]{1,99}$", last_name):
        return jsonify({
            "status": "failure",
            "reason": "Неверная фамилия"
        });
    if email_address != "" and not re.match("^[a-zA-Z0-9._-]+@[a-zA-Z]+\.[a-zA-Z]{2,3}$", email_address):
        return jsonify({
            "status": "failure",
            "reason": "Неверный адрес электронной почты"
        });
    if phone_number != "" and not re.match("^\+[0-9]{3}-[0-9]{2}-[0-9]{7}$", phone_number):
        return jsonify({
            "status": "failure",
            "reason": "Неверный номер телефона"
        });
    if not re.match("^[1-9]{1}[0-9]*$", new_user_role_id):
        return jsonify({
            "status": "failure",
            "reason": "role_id не является числом"
        });
    query = "SELECT id FROM geomap.users WHERE username = %s";
    g.cur.execute(query, [username]);
    rows = g.cur.fetchall();
    if len(rows) > 0:
        result = {
            "status": "failure",
            "reason": "Имя пользователя уже занято"
        }
        return jsonify(result);
    query = "SELECT id FROM geomap.roles WHERE id = %s";
    g.cur.execute(query, [new_user_role_id]);
    rows = g.cur.fetchall();
    if len(rows) == 0:
        return jsonify({
            "status": "failure",
            "reason": "Неверный идетификатор для role_id"
        });
    user_id = None
    try:
        print "LOCKING TABLES users"
        lock_tables(g.cur, ["users", "settings"], "WRITE");
        query = "INSERT INTO geomap.users(user_first_name, user_last_name, phone_number, email_address, username, password, role_id, enabled) VALUES(%s, %s, %s, %s, %s, SHA2(%s, 256), %s, FALSE);";
        salted_password = password + config["PASSWORD_SALT"];
        g.cur.execute(query, [first_name, last_name, phone_number, email_address, username, salted_password,
                              new_user_role_id]);
        g.db.commit();
        query = "SELECT id FROM geomap.users WHERE username = %s";
        g.cur.execute(query, [username]);
        row = g.cur.fetchone();
        if not row:
            raise
        user_id = row["id"];
        # This should be populated with various default values
        query = """
			INSERT INTO geomap.settings(user_id, vkey, value) VALUES(%s, "range", "100000");
			INSERT INTO geomap.settings(user_id, vkey, value) VALUES(%s, "bgcolor", "4da6ff");
			INSERT INTO geomap.settings(user_id, vkey, value) VALUES(%s, "checkinterval", "120000");
			INSERT INTO geomap.settings(user_id, vkey, value) VALUES(%s, "showsidepanel", "false");
		"""
        params = [user_id for i in range(0, 4)];
        g.cur.execute(query, params)
    except:
        return jsonify({
            "status": "failure",
            "reason": "Внутренняя ошибка сервера"
        });
    finally:
        print "UNLOCKING TABLES users"
        unlock_tables(g.cur);
    # query = "SELECT id FROM geomap.users WHERE username = %s";
    # g.cur.execute(query, [username]);
    # row = g.cur.fetchone();
    end_time = datetime.datetime.now();
    query_stats("/api/add_user/", (end_time - start_time).total_seconds());
    if not user_id:
        return jsonify({
            "status": "failure",
            "reason": "Ошибка при регистрации пользователя"
        });
    else:
        # user_id = row["id"];
        return jsonify({
            "status": "success",
            "user_id": user_id
        });


@app.route("/api/update_user/", methods=["POST"])
def update_user():
    start_time = datetime.datetime.now();
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    try:
        data = json.loads(request.stream.read());
    except:
        return Utils.make_response({
            "status": "failure",
            "reason": "Ошибка при декодировании JSON объекта"
        }, 200);
    user_id = data.get("user_id") or "";
    first_name = data.get("first_name") or "";
    last_name = data.get("last_name") or "";
    phone_number = data.get("phone_number") or "";
    email_address = data.get("email_address") or "";
    role_id = data.get("role_id") or "";
    enabled = data.get("enabled") or False;
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if not ip_based_authorization(remote_ip):
        return jsonify({"status": "failure", "reason": "forbidden"});
    if authorize("/api/update_user/", token, "modify", remote_ip, remote_port) != True:
        register_authorization_failure("/api/update_user/", token);
        return jsonify({"status": "failure", "reason": "forbidden"});
    if not re.match("^[1-9]{1}[0-9]*$", role_id):
        return jsonify({
            "status": "failure",
            "reason": "Неверная роль пользователя"
        });
    if not re.match("^[1-9]{1}[0-9]*$", user_id):
        return jsonify({
            "status": "failure",
            "reason": "Неверное имя пользователя"
        });
    if first_name != "" and not re.match("^[A-Z]{1}[a-z]{1,99}$", first_name):
        return jsonify({
            "status": "failure",
            "reason": "Неверное имя"
        });
    if last_name != "" and not re.match("^[A-Z]{1}[a-z]{1,99}$", last_name):
        return jsonify({
            "status": "failure",
            "reason": "Неверная фамилия"
        });
    if email_address != "" and not re.match("^[a-zA-Z0-9._-]+@[a-zA-Z]+\.[a-zA-Z]{2,3}$", email_address):
        return jsonify({
            "status": "failure",
            "reason": "Неверный адрес электронной почты"
        });
    if phone_number != "" and not re.match("^\+[0-9]{3}-[0-9]{2}-[0-9]{7}$", phone_number):
        return jsonify({
            "status": "failure",
            "reason": "Неверный номер телефона"
        });
    query = "SELECT id FROM geomap.roles WHERE id = %s";
    g.cur.execute(query, [role_id]);
    row = g.cur.fetchone();
    if not row:
        return jsonify({
            "status": "failure",
            "reason": "Неверная роль пользователя"
        });
    query = "SELECT id FROM geomap.users WHERE id = %s";
    g.cur.execute(query, [user_id]);
    rows = g.cur.fetchall();
    if len(rows) == 0:
        result = {
            "status": "failure",
            "reason": "Пользователь не существует"
        }
        return jsonify(result);
    params = [];
    query = "UPDATE geomap.users SET role_id = %s, enabled = %s, ";
    params.append(role_id);
    params.append(enabled);
    if first_name != "":
        query += "user_first_name = %s,";
        params.append(first_name);
    if last_name != "":
        query += "user_last_name = %s,";
        params.append(last_name);
    if phone_number != "":
        query += "phone_number = %s, ";
        params.append(phone_number);
    if email_address != "":
        query += "email_address = %s ";
        params.append(email_address);
    if query[len(query) - 1] == ",":
        query = query.rstrip(",");
    if first_name == "" and last_name == "" and phone_number == "" and email_address == "":
        return jsonify({
            "status": "failure",
            "reason": "Данные не изменены"
        })
    query += "WHERE id = %s";
    params.append(user_id);
    try:
        print "LOCKING TABLES users"
        lock_tables(g.cur, ["users"], "WRITE");
        g.cur.execute(query, params);
        g.db.commit();
        print g.cur._last_executed
        result = {
            "status": "success"
        }
    except Exception as e:
        result = {
            "status": "failure",
            "reason": "Внутренняя ошибка сервера"
        }
    finally:
        print "UNLOCKING TABLES users"
        unlock_tables(g.cur);
    end_time = datetime.datetime.now();
    query_stats("/api/update_user/", (end_time - start_time).total_seconds());
    return jsonify(result);


@app.route("/api/delete_user/", methods=["DELETE"])
def delete_user():
    start_time = datetime.datetime.now();
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    try:
        data = json.loads(request.stream.read());
    except:
        return Utils.make_response({
            "status": "failure",
            "reason": "Ошибка при декодировании JSON объекта"
        }, 200);
    user_id = data.get("user_id") or "";
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if not ip_based_authorization(remote_ip):
        return jsonify({"status": "failure", "reason": "forbidden"});
    if authorize("/api/delete_user/", token, "delete", remote_ip, remote_port) != True:
        register_authorization_failure("/api/delete_user/", token);
        return jsonify({"status": "failure", "reason": "forbidden"});
    if not re.match("^[1-9]{1}[0-9]*$", user_id):
        return jsonify({
            "status": "failure",
            "reason": "Неверное имя пользователя"
        });
    query = "SELECT username FROM geomap.users WHERE id = %s";
    g.cur.execute(query, [user_id]);
    rows = g.cur.fetchall();
    if len(rows) == 0:
        return jsonify({
            "status": "failure",
            "reason": "Пользователь не найден"
        }
        );
    username = rows[0]["username"];
    if re.match("^admin$", username):
        return jsonify({
            "status": "failure",
            "reason": "Нельзя удалить системного пользователя"
        });
    try:
        print "LOCKING TABLES users"
        lock_tables(g.cur, ["users"], "WRITE");
        query = "DELETE FROM geomap.users WHERE id = %s";
        g.cur.execute(query, [user_id]);
        g.db.commit();
    except:
        return jsonify({
            "status": "failure",
            "reason": "Внутренняя ошибка сервера"
        });
    finally:
        print "UNLOCKING TABLES users"
        unlock_tables(g.cur);
    end_time = datetime.datetime.now();
    query_stats("/api/delete_user/", (end_time - start_time).total_seconds());
    return jsonify({
        "status": "success"
    });


@app.route("/api/get_users/")
def get_users():
    start_time = datetime.datetime.now();
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if not ip_based_authorization(remote_ip):
        return jsonify({"status": "failure", "reason": "forbidden"});
    if authorize("/api/get_users/", token, "read", remote_ip, remote_port) != True:
        register_authorization_failure("/api/get_users/", token);
        return jsonify({"status": "failure", "reason": "forbidden"});
    query = "SELECT id, username, user_first_name, user_last_name, phone_number, email_address FROM geomap.users";
    g.cur.execute(query);
    rows = g.cur.fetchall();
    data = dict();
    for row in rows:
        data[row["id"]] = {
            "username": row["username"],
            "user_first_name": row["user_first_name"],
            "user_last_name": row["user_last_name"],
            "phone_number": row["phone_number"],
            "email_address": row["email_address"]
        };
    end_time = datetime.datetime.now();
    query_stats("/api/get_users/", (end_time - start_time).total_seconds());
    return jsonify({
        "status": "success",
        "data": data
    });


@app.route("/api/get_user/")
def get_user():
    start_time = datetime.datetime.now();
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    user_id = request.args.get("user_id") or "";
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if not ip_based_authorization(remote_ip):
        return jsonify({"status": "failure", "reason": "forbidden"});
    if authorize("/api/get_user/", token, "read", remote_ip, remote_port) != True:
        register_authorization_failure("/api/get_user/", token);
        return jsonify({"status": "failure", "reason": "forbidden"});
    if not re.match("^[1-9]{1}[0-9]*$", user_id):
        return jsonify({
            "status": "failure",
            "reason": "Неверный идентификатор пользователя"
        })
    query = "SELECT id, username, user_first_name, user_last_name, phone_number, email_address, role_id, enabled FROM geomap.users WHERE id = %s";
    g.cur.execute(query, [user_id]);
    row = g.cur.fetchone();
    data = dict();
    if row:
        data[row["id"]] = {
            "username": row["username"],
            "user_first_name": row["user_first_name"],
            "user_last_name": row["user_last_name"],
            "phone_number": row["phone_number"],
            "email_address": row["email_address"],
            "role_id": row["role_id"],
            "enabled": row["enabled"]
        };
    end_time = datetime.datetime.now();
    query_stats("/api/get_user/", (end_time - start_time).total_seconds());
    return jsonify({
        "status": "success",
        "data": data
    });


@app.route("/api/get_deposit_statuses/")
def get_deposit_statuses():
    start_time = datetime.datetime.now();
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if authorize("/api/get_deposit_statuses/", token, "read", remote_ip, remote_port) != True:
        register_authorization_failure("/api/get_deposit_statuses/", token);
        return jsonify({"status": "failure", "reason": "forbidden"});
    query = "SELECT id, name_ru, name_en, name_uz FROM geomap.deposit_status";
    g.cur.execute(query);
    result = [{
        "id": -1,
        "status_name_en": "All",
        "status_name_ru": "Все",
        "status_name_uz": ""
    }];
    for row in g.cur.fetchall():
        result.append({
            "id": row["id"],
            "status_name_en": row["name_en"],
            "status_name_ru": row["name_ru"],
            "status_name_uz": row["name_uz"]
        });
    end_time = datetime.datetime.now();
    query_stats("/api/get_deposit_statuses/", (end_time - start_time).total_seconds());
    return jsonify({
        "status": "success",
        "data": result,
        "authenticated": (True if token else False)
    });


@app.route("/api/change_password/", methods=["POST"])
def change_password():
    start_time = datetime.datetime.now();
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    try:
        data = json.loads(request.stream.read());
    except:
        return Utils.make_response({
            "status": "failure",
            "reason": "Ошибка при декодировании JSON объекта"
        }, 200);
    user_id = data.get("user_id") or "";
    new_password = data.get("new_password") or "";
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if not ip_based_authorization(remote_ip):
        return jsonify({"status": "failure", "reason": "forbidden"});
    if authorize("/api/change_password/", token, "modify", remote_ip, remote_port) != True:
        register_authorization_failure("/api/change_password/", token);
        return jsonify({"status": "failure", "reason": "forbidden"});
    if not re.match("^[0-9]{1}[0-9]*$", user_id):
        return jsonify({
            "status": "failure",
            "reason": "Неверное имя пользователя"
        });
    if not re.match("^(?=.*[A-Z]+)(?=.*[a-z]+)(?=.*[0-9]+)(?=.*[$#%]+)", new_password) or not re.match(
            "^[a-zA-Z0-9#$%&@]{10,100}$", new_password):
        return jsonify({
            "status": "failure",
            "reason": "Неверный пароль"
        });
    query = "SELECT id FROM geomap.users WHERE id = %s";
    g.cur.execute(query, [user_id]);
    rows = g.cur.fetchall();
    if len(rows) == 0:
        return jsonify({
            "status": "failure",
            "reason": "Имя пользователя не ныйдено"
        });
    salted_password = new_password + config["PASSWORD_SALT"];
    query = "SELECT id FROM geomap.users WHERE id = %s AND password = SHA2(%s, 256)";
    g.cur.execute(query, [user_id, salted_password]);
    rows = g.cur.fetchall();
    if len(rows) != 0:
        return jsonify({
            "status": "failure",
            "reason": "Новый пароль должен отличаться от предыдущего"
        });
    try:
        print "LOCKING TABLES users, auth_tokens"
        lock_tables(g.cur, ["users", "auth_tokens"], "WRITE");
        query = "UPDATE geomap.users SET password = SHA2(%s, 256) WHERE id = %s";
        g.cur.execute(query, [salted_password, user_id]);
        g.db.commit();
        # Reset all previously active logins
        query = "DELETE FROM geomap.auth_tokens WHERE user_id = %s";
        g.cur.execute(query, [user_id]);
        g.db.commit();
    except:
        return jsonify({
            "status": "failure",
            "reason": "Внутренняя ошибка сервера"
        });
    finally:
        print "UNLOCKING TABLES users, auth_tokens"
        unlock_tables(g.cur);
    end_time = datetime.datetime.now();
    query_stats("/api/change_password/", (end_time - start_time).total_seconds());
    return jsonify({
        "status": "success"
    });


@app.route("/api/regions/")
def get_list_of_regions():
    start_time = datetime.datetime.now();
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if authorize("/api/regions/", token, "read", remote_ip, remote_port) != True:
        register_authorization_failure("/api/regions/", token)
        return jsonify({"status": "failure", "reason": "forbidden"});
    role_id = get_role_for_token(token, remote_ip);
    query = "SELECT a.region_id AS id, a.name_en, a.name_ru, a.name_uz FROM areas a INNER JOIN permissions p ON p.resource_id = a.resource_id WHERE a.area_id = 0 AND p.role_id = %s AND p.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')";
    g.cur.execute(query, [role_id]);
    result = [{
        "id": -1,
        "region_name_en": "All",
        "region_name_ru": "Все",
        "region_name_uz": ""
    }];
    for row in g.cur.fetchall():
        result.append({
            "id": row["id"],
            "region_name_en": row["name_en"],
            "region_name_ru": row["name_ru"],
            "region_name_uz": row["name_uz"]
        });
    end_time = datetime.datetime.now();
    query_stats("/api/regions/", (end_time - start_time).total_seconds());
    return jsonify({
        "status": "success",
        "data": result,
        "authenticated": (True if token else False)
    });


@app.route("/api/areas/")
def get_list_of_areas():
    start_time = datetime.datetime.now();
    region_id = request.args.get("region_id") or "";
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if authorize("/api/areas/", token, "read", remote_ip, remote_port) != True:
        register_authorization_failure("/api/areas/", token)
        return jsonify({"status": "failure", "reason": "forbidden"});
    role_id = get_role_for_token(token, remote_ip);
    query = "".join(
        [
            "SELECT a.area_id AS id, a.region_id, a.name_en, ",
            "a.name_ru, a.name_uz FROM areas a INNER JOIN permissions p ON p.resource_id = a.resource_id WHERE a.region_id = %s AND a.area_id != 0 AND p.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read') AND p.role_id = %s",
        ]);
    result = [{
        "id": -1,
        "region_id": -1,
        "area_name_en": "All",
        "area_name_ru": "Все",
        "area_name_uz": ""
    }];
    if region_id == "" or region_id == "-1":
        return jsonify({
            "status": "success",
            "data": result,
            "authenticated": (True if token else False)
        });
    if not re.match("^[1-9]{1}[0-9]*$", region_id):
        return jsonify({
            "status": "failure",
            "reason": "Неверная область"
        });
    g.cur.execute(query, [region_id, role_id]);
    for row in g.cur.fetchall():
        result.append({
            "id": row["id"],
            "region_id": row["region_id"],
            "area_name_en": row["name_en"],
            "area_name_ru": row["name_ru"],
            "area_name_uz": row["name_uz"]
        });
    end_time = datetime.datetime.now();
    query_stats("/api/areas/", (end_time - start_time).total_seconds());
    return jsonify({
        "status": "success",
        "data": result,
        "authenticated": (True if token else False)
    });


@app.route("/api/minerals/")
def get_list_of_minerals():
    start_time = datetime.datetime.now();
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if authorize("/api/minerals/", token, "read", remote_ip, remote_port) != True:
        register_authorization_failure("/api/minerals/", token)
        return jsonify({"status": "failure", "reason": "forbidden"});
    role_id = get_role_for_token(token, remote_ip);
    query = "SELECT m.id, m.name_uz, m.name_ru, m.name_en FROM minerals m INNER JOIN permissions p ON p.resource_id = m.resource_id WHERE p.role_id = %s AND p.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read') ORDER BY name_ru ASC";
    g.cur.execute(query, [role_id]);
    result = [{
        "id": -1,
        "mineral_name_en": "All",
        "mineral_name_ru": "Все",
        "mineral_name_uz": ""
    }];
    for row in g.cur.fetchall():
        result.append({
            "id": row["id"],
            "mineral_name_en": row["name_en"],
            "mineral_name_ru": row["name_ru"],
            "mineral_name_uz": row["name_uz"]
        });
    end_time = datetime.datetime.now();
    query_stats("/api/minerals/", (end_time - start_time).total_seconds());
    return jsonify({
        "status": "success",
        "data": result,
        "authenticated": (True if token else False)
    });


@app.route("/api/region_borders/")
def get_region_borders():
    start_time = datetime.datetime.now();
    region_id = request.args.get("region_id") or "";
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if authorize("/api/region_borders/", token, "read", remote_ip, remote_port) != True:
        register_authorization_failure("/api/region_borders/", token)
        return jsonify({"status": "failure", "reason": "forbidden"});
    role_id = get_role_for_token(token, remote_ip);
    query = "".join((
        "SELECT a.name_ru, rl.latitude, rl.longitude ",
        "FROM region_location AS rl JOIN areas AS a ",
        "ON a.id=rl.region_id ",
        "INNER JOIN permissions p ON p.resource_id = rl.resource_id ",
        "WHERE a.area_id = 0 AND p.role_id = %s AND p.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read') "
    ));
    print query
    if region_id == "-1" or region_id == "":
        g.cur.execute(query, [role_id])
    else:
        query = "".join((query, "AND a.region_id = %s"))
        if not re.match("^[1-9]{1}[0-9]*$", region_id):
            return jsonify({
                "status": "failure",
                "reason": "Неверная область"
            });
        g.cur.execute(query, [role_id, region_id])
    result = dict();

    for row in g.cur.fetchall():
        if row["name_ru"] in result.keys():
            result[row["name_ru"]].append({
                "lat": float(row["latitude"]),
                "lng": float(row["longitude"])
            });
        else:
            result[row["name_ru"]] = []
            result[row["name_ru"]].append({
                "lat": float(row["latitude"]),
                "lng": float(row["longitude"])
            });
    end_time = datetime.datetime.now();
    query_stats("/api/region_borders/", (end_time - start_time).total_seconds());
    return jsonify({
        "status": "success",
        "data": result,
        "authenticated": (True if token else False)
    });


@app.route("/api/region_decorations/")
def get_region_decorations():
    start_time = datetime.datetime.now();
    region_id = request.args.get("region_id") or "";
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if authorize("/api/region_decorations/", token, "read", remote_ip, remote_port) != True:
        register_authorization_failure("/api/region_decorations/", token)
        return jsonify({"status": "failure", "reason": "forbidden"});
    role_id = get_role_for_token(token, remote_ip);
    query = "".join((
        "SELECT a.name_ru, rd.color, rd.center_latitude, rd.center_longitude, ",
        "rd.opacity_on_mouse_out, rd.opacity_on_mouse_over, ",
        "rd.bound_north_east_lat, rd.bound_north_east_lng, ",
        "rd.bound_south_west_lat, rd.bound_south_west_lng, a.region_id ",
        "FROM region_decorations AS rd INNER JOIN ",  # areas AS a
        "(SELECT aa.id, aa.name_ru, aa.region_id, aa.area_id, aa.resource_id FROM geomap.areas aa INNER JOIN permissions pp ON aa.resource_id = pp.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS a "
        "ON a.id=rd.area_region_id ",
        "INNER JOIN permissions p ON p.resource_id = rd.resource_id ",
        "WHERE a.area_id = 0 AND p.role_id = %s AND p.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read') "
    ));
    if region_id == "-1" or region_id == "":
        g.cur.execute(query, [role_id, role_id])
    else:
        if not re.match("^[1-9]{1}[0-9]*$", region_id):
            return jsonify({
                "status": "failure",
                "reason": "Неверная область"
            });
        query = "".join((query, "AND a.region_id = %s"))
        g.cur.execute(query, [role_id, role_id, region_id])

    result = dict();
    for row in g.cur.fetchall():
        result[row["name_ru"]] = {
            "region_id": row["region_id"],
            "fill_color": row["color"],
            "stroke_color": row["color"],
            "center_latitude": float(row["center_latitude"]),
            "center_longitude": float(row["center_longitude"]),
            "opacity_on_mouse_out": float(row["opacity_on_mouse_out"]),
            "opacity_on_mouse_over": float(row["opacity_on_mouse_over"]),
            "bounds": {
                "northEast": {
                    "lat": float(row["bound_north_east_lat"]),
                    "lng": float(row["bound_north_east_lng"])
                },
                "southWest": {
                    "lat": float(row["bound_south_west_lat"]),
                    "lng": float(row["bound_south_west_lng"])
                }
            }
        };
    end_time = datetime.datetime.now();
    query_stats("/api/region_decorations/", (end_time - start_time).total_seconds());
    return jsonify({
        "status": "success",
        "data": result,
        "authenticated": (True if token else False)
    });


@app.route("/api/get_image/")
def get_image_by_id():
    start_time = datetime.datetime.now();
    uuid = request.args.get("uuid") or "";
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if authorize("/api/get_image/", token, "read", remote_ip, remote_port) != True:
        register_authorization_failure("/api/get_image/", token)
        return jsonify({"status": "failure", "reason": "forbidden"});
    role_id = get_role_for_token(token, remote_ip);
    result = {}
    if uuid != None:
        if not re.match("^[0-9]+$", uuid):
            return jsonify({
                "status": "failure",
                "reason": "Неверный UUID"
            });
        query = "SELECT i.id as uuid, i.data, i.name FROM images AS i INNER JOIN permissions p ON p.resource_id = i.resource_id WHERE i.id = %s AND p.role_id = %s AND p.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')";
        params = [uuid, role_id];
        g.cur.execute(query, params);
        row = g.cur.fetchone();
        if not row:
            return jsonify({
                "data": {},
                "authenticated": (True if token else False)
            });
        result["uuid"] = uuid;
        result["data"] = row["data"];
        result["name"] = row["name"];
    else:
        return jsonify({});
    end_time = datetime.datetime.now();
    query_stats("/api/get_image/", (end_time - start_time).total_seconds());
    return jsonify({
        "status": "success",
        "data": result,
        "authenticated": (True if token else False)
    });


@app.route("/api/resources_from_point/")
def get_list_of_resources_from_point():
    start_time = datetime.datetime.now();
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if authorize("/api/resources_from_point/", token, "read", remote_ip, remote_port) != True:
        register_authorization_failure("/api/resources_from_point/", token)
        return jsonify({"status": "failure", "reason": "forbidden"});
    role_id = get_role_for_token(token, remote_ip);
    region_id = request.args.get("region_id") or "";
    area_id = request.args.get("area_id") or "";
    resource_kind = request.args.get("resource_kind") or "";
    resource_group = request.args.get("resource_group") or "";
    resource_type = request.args.get("resource_type") or "";
    resource_subtype = request.args.get("resource_subtype") or "";
    numClusters = request.args.get("num_clusters");
    latitude = request.args.get("latitude");
    longitude = request.args.get("longitude");
    distance = request.args.get("distance");
    status_id = request.args.get("status_id") or "";
    remainder_id = request.args.get("remainder_id") or "";
    try:
        latitude = float(latitude);
        if latitude < 0 or latitude > 90:
            return jsonify({
                "status": "failure",
                "reason": "Широта должна быть больше или равна 0 и меньше или равна 90 градусов"
            });
    except:
        return jsonify({
            "status": "failure",
            "reason": "Неверная широта"
        });
    try:
        longitude = float(longitude)
        if longitude < 0 or longitude > 180:
            return jsonify({
                "status": "failure",
                "reason": "Долгота должна быть больше или равна 0 и меньше или равна 180 градусов"
            });
    except:
        return jsonify({
            "status": "failure",
            "reason": "Неверная долгота"
        });
    try:
        distance = float(distance)
        if distance <= 0:
            return jsonify({
                "status": "failure",
                "reason": "Дистанция должна быть больше 0"
            });
    except:
        return jsonify({
            "status": "failure",
            "reason": "Дистанция должна быть числом"
        });
    try:
        numClusters = int(numClusters);
    except:
        numClusters = "All";
    numIterations = 1;
    params = [];
    initial_centroids = [
        [decimal.Decimal(40.765186), decimal.Decimal(72.328148)],
        [decimal.Decimal(40.497619), decimal.Decimal(71.275501)],
        [decimal.Decimal(40.172620), decimal.Decimal(63.638184)],
        [decimal.Decimal(43.676161), decimal.Decimal(59.001625)],
        [decimal.Decimal(40.406000), decimal.Decimal(68.671899)],
        [decimal.Decimal(39.875773), decimal.Decimal(66.387894)],
        [decimal.Decimal(41.203339), decimal.Decimal(69.765714)],
        [decimal.Decimal(40.979924), decimal.Decimal(71.225837)],
        [decimal.Decimal(38.831461), decimal.Decimal(66.162693)],
        [decimal.Decimal(40.131718), decimal.Decimal(67.823338)],
        [decimal.Decimal(41.521693), decimal.Decimal(64.241037)],
        [decimal.Decimal(41.513229), decimal.Decimal(60.629134)],
        [decimal.Decimal(38.021292), decimal.Decimal(67.475130)]
    ];

    # NOT TESTED PROPERLY YET
    lat1 = findLatLongFromPointAndDistance([latitude, longitude], 0, distance / 2.0)[0];
    long1 = findLatLongFromPointAndDistance([latitude, longitude], 270, distance / 2.0)[1];
    lat2 = findLatLongFromPointAndDistance([latitude, longitude], 180, distance / 2.0)[0];
    long2 = findLatLongFromPointAndDistance([latitude, longitude], 90, distance / 2.0)[1];

    query = "".join((
        "SELECT dst.id, d.name_en AS deposit_name_en, d.name_ru  AS deposit_name_ru, " \
        "d.name_uz AS deposit_name_uz, a.name_en AS area_name_en, a.name_ru AS area_name_ru, " \
        "a.name_uz AS area_name_uz, a.name_en AS area_name_en, s.name_ru AS site_name_ru, " \
        "s.name_uz AS site_name_uz, s.name_en AS site_name_en, ds.latitude, ds.longitude, " \
        "(SELECT aa.name_ru FROM geomap.areas aa WHERE aa.region_id = a.region_id AND aa.area_id = 0) AS region_name_ru, " \
        "(SELECT aa.name_en FROM geomap.areas aa WHERE aa.region_id = a.region_id AND aa.area_id = 0) AS region_name_en, " \
        "(SELECT aa.name_uz FROM geomap.areas aa WHERE aa.region_id = a.region_id AND aa.area_id = 0) AS region_name_uz " \
        "FROM geomap.deposits_sites ds " \
        "INNER JOIN (SELECT dd.id, dd.name_ru, dd.name_uz, dd.name_en FROM geomap.deposits dd INNER JOIN geomap.permissions pp ON pp.resource_id = dd.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS d " \
        "ON ds.deposit_id = d.id " \
        "INNER JOIN (SELECT ss.id, ss.name_ru, ss.name_uz, ss.name_en FROM geomap.sites ss INNER JOIN geomap.permissions pp ON pp.resource_id = ss.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS s " \
        "ON ds.site_id = s.id " \
        "INNER JOIN (SELECT ddst.id, ddst.deposit_site_id, ddst.type_group_id, ddst.minerals_id, ddst.status_id, ddst.amount_a_b_c1, ddst.amount_c2 FROM geomap.deposits_sites_types ddst INNER JOIN geomap.permissions pp ON pp.resource_id = ddst.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS dst " \
        "ON ds.id = dst.deposit_site_id " \
        "INNER JOIN (SELECT dtdt.id, dtdt.kind_id, dtdt.group_id, dtdt.type_id, dtdt.subtype_id FROM geomap.deposit_types dtdt INNER JOIN geomap.permissions pp ON pp.resource_id = dtdt.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS dt " \
        "ON dt.id = dst.type_group_id " \
        "INNER JOIN (SELECT aa.id, aa.name_ru, aa.name_uz, aa.name_en, aa.region_id, aa.area_id FROM geomap.areas aa INNER JOIN geomap.permissions pp ON pp.resource_id = aa.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS a " \
        "ON a.id = ds.region_area_id " \
        "INNER JOIN permissions p ON p.resource_id = ds.resource_id " \
        "WHERE p.role_id = %s AND p.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read') "
    ));

    null = [params.append(role_id) for x in range(0, 6)];
    if resource_kind != "" and resource_kind != "-1":
        if not re.match("^[1-9]{1}[0-9]*$", resource_kind):
            return jsonify({
                "status": "failure",
                "reason": "Неверный вид полезного ископаемого"
            });
        query = "".join((query,
                         "AND dt.kind_id = %s AND 0 < (SELECT COUNT(*) FROM deposit_types dtdt INNER JOIN permissions pp ON dtdt.resource_id = pp.resource_id WHERE dtdt.kind_id = %s AND dtdt.group_id = 0 AND dtdt.type_id = 0 AND dtdt.subtype_id = 0 AND pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) "));
        params.append(resource_kind);
        params.append(resource_kind);
        params.append(role_id);
        if resource_group != "" and resource_group != "-1":
            if not re.match("^[1-9]{1}[0-9]*$", resource_group):
                return jsonify({
                    "status": "failure",
                    "reason": "Неверная группа полезного ископаемого"
                });
            query = "".join((query,
                             "AND dt.group_id = %s AND 0 < (SELECT COUNT(*) FROM deposit_types dtdt INNER JOIN permissions pp ON dtdt.resource_id = pp.resource_id WHERE dtdt.kind_id = %s AND dtdt.group_id = %s AND pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) "))
            params.append(resource_group);
            params.append(resource_kind);
            params.append(resource_group);
            params.append(role_id);
            if resource_type != "" and resource_type != "-1":
                if not re.match("^[1-9]{1}[0-9]*$", resource_type):
                    return jsonify({
                        "status": "failure",
                        "reason": "Неверный тип полезного ископаемого"
                    });
                query = "".join((query,
                                 "AND dt.type_id = %s AND 0 < (SELECT COUNT(*) FROM deposit_types dtdt INNER JOIN permissions pp ON dtdt.resource_id = pp.resource_id WHERE dtdt.kind_id = %s AND dtdt.group_id = %s AND dtdt.type_id = %s AND pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) "))
                params.append(resource_type);
                params.append(resource_kind);
                params.append(resource_group);
                params.append(resource_type);
                params.append(role_id);
                if resource_subtype != "" and resource_subtype != "-1":
                    if not re.match("^[1-9]{1}[0-9]*$", resource_subtype):
                        return jsonify({
                            "status": "failure",
                            "reason": "Неверный подтип полезного ископаемого"
                        });
                    query = "".join((query, "AND dt.subtype_id = %s "))
                    params.append(resource_subtype);
            else:
                query = "".join((query,
                                 "AND 0 < (SELECT COUNT(*) FROM deposit_types dtdt INNER JOIN permissions pp ON dtdt.resource_id = pp.resource_id WHERE dtdt.kind_id = %s AND dtdt.group_id = %s AND pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) "))
                params.append(resource_kind);
                params.append(resource_group);
                params.append(role_id);
        else:
            query = "".join((query,
                             "AND 0 < (SELECT COUNT(*) FROM deposit_types dtdt INNER JOIN permissions pp ON dtdt.resource_id = pp.resource_id WHERE dtdt.kind_id = %s AND pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) "))
            params.append(resource_kind);
            params.append(role_id);
    else:
        query = "".join((query,
                         "AND 0 < (SELECT COUNT(*) FROM deposit_types dtdt INNER JOIN permissions pp ON dtdt.resource_id = pp.resource_id WHERE dtdt.kind_id <> 0 AND dtdt.group_id = 0 AND dtdt.type_id = 0 AND dtdt.subtype_id = 0 AND pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) "));
        params.append(role_id);
    if region_id != "" and region_id != "-1":
        if not re.match("^[1-9]{1}[0-9]*$", region_id):
            return jsonify({
                "status": "failure",
                "reason": "Неверная область"
            });
        query = "".join((query, "AND a.region_id = %s "))
        params.append(region_id);
        if area_id != "" and area_id != "-1":
            if not re.match("^[1-9]{1}[0-9]*$", area_id):
                return jsonify({
                    "status": "failure",
                    "reason": "Неверный район"
                });
            query = "".join((query, "AND a.area_id = %s "))
            params.append(area_id);
    if remainder_id != "" and remainder_id != "-1":
        if not re.match("^(1|2)$", remainder_id):
            return jsonify({
                "status": "failure",
                "reason": "Неверный идентификатор для остатка"
            });
        if remainder_id == "1":
            query = "".join((query, "AND (dst.amount_a_b_c1 > 0 OR dst.amount_c2 > 0) "))
        if remainder_id == "2":
            query = "".join((query, "AND dst.amount_a_b_c1 = 0 AND dst.amount_c2 = 0 "))
    if status_id != "" and status_id != "-1":
        if not re.match("^[1-9]{1}[0-9]*$", status_id):
            return jsonify({
                "status": "failure",
                "reason": "Неверный статус"
            });
        query = "".join((query, "AND dst.status_id = %s "));
        params.append(status_id);
    query = "".join(
        (query, "AND ds.latitude <= %s AND ds.longitude >= %s AND ds.latitude >= %s AND ds.longitude <= %s "))
    params.append(lat1);
    params.append(long1);
    params.append(lat2);
    params.append(long2);
    # print query
    query = "".join((query, "ORDER BY deposit_name_ru"))
    g.cur.execute(query, params);
    print g.cur._last_executed
    result = [];
    X = [];
    Y = [];
    seen_ids = {};
    IDS = [];
    for row in g.cur.fetchall():
        X.append(decimal.Decimal(row["latitude"]));
        Y.append(decimal.Decimal(row["longitude"]));
        IDS.append(row["id"]);
        seen_ids[row["id"]] = {
            "ID": row["id"],
            "deposit_name_en": row["deposit_name_en"],
            "deposit_name_ru": row["deposit_name_ru"],
            "deposit_name_uz": row["deposit_name_uz"],
            "region_name_en": row["region_name_en"],
            "region_name_ru": row["region_name_ru"],
            "region_name_uz": row["region_name_uz"],
            "area_name_en": row["area_name_en"],
            "area_name_ru": row["area_name_ru"],
            "area_name_uz": row["area_name_uz"],
            "site_name_en": row["site_name_en"],
            "site_name_ru": row["site_name_ru"],
            "site_name_uz": row["site_name_uz"],
            "location": {
                "lat": float(row["latitude"]),
                "lng": float(row["longitude"]),
                "coordinate_x": float(0),
                "coordinate_y": float(0),
                "zone": int(0)
            }
        }
    clustering = KMeansClustering();
    clusters = {};
    centroids = {};

    # if numClusters == "All":
    numClusters = len(X);
    if len(X) < numClusters:
        numClusters = len(X);
    if len(X) > 0:
        if numClusters == len(initial_centroids):
            X = np.array(list(zip(X, Y)), dtype=np.dtype(decimal.Decimal));
            out = clustering.clusterPredifinedCentroids(X, initial_centroids, numIterations);
        else:
            out = clustering.clusterRandomCentroids(X, Y, numClusters, numIterations);
    index = 0;
    for id in IDS:
        seen_ids[id]["cluster"] = out["clusters"][index];
        seen_ids[id]["centroid"] = {
            "lat": float(out["centroids"][index][0]),
            "lng": float(out["centroids"][index][1])
        };
        result.append(seen_ids[id]);
        index += 1;
    end_time = datetime.datetime.now();
    query_stats("/api/resources_from_point/", (end_time - start_time).total_seconds());
    return jsonify({
        "status": "success",
        "data": result,
        "authenticated": (True if token else False)
    });


@app.route("/api/resources/")
def get_list_of_resources():
    start_time = datetime.datetime.now();
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if authorize("/api/resources/", token, "read", remote_ip, remote_port) != True:
        register_authorization_failure("/api/resources/", token)
        return jsonify({"status": "failure", "reason": "forbidden"});
    role_id = get_role_for_token(token, remote_ip);
    region_id = request.args.get("region_id") or "";
    area_id = request.args.get("area_id") or "";
    resource_kind = request.args.get("resource_kind") or "";
    resource_group = request.args.get("resource_group") or "";
    resource_type = request.args.get("resource_type") or "";
    resource_subtype = request.args.get("resource_subtype") or "";
    resource_name = request.args.get("resource_name") or "";
    language = request.args.get("language") or "";
    numClusters = request.args.get("num_clusters");
    status_id = request.args.get("status_id") or "";
    remainder_id = request.args.get("remainder_id") or "";
    try:
        numClusters = int(numClusters);
    except:
        numClusters = "All";
    numIterations = 1;
    params = [];
    initial_centroids = [
        [decimal.Decimal(40.765186), decimal.Decimal(72.328148)],
        [decimal.Decimal(40.497619), decimal.Decimal(71.275501)],
        [decimal.Decimal(40.172620), decimal.Decimal(63.638184)],
        [decimal.Decimal(43.676161), decimal.Decimal(59.001625)],
        [decimal.Decimal(40.406000), decimal.Decimal(68.671899)],
        [decimal.Decimal(39.875773), decimal.Decimal(66.387894)],
        [decimal.Decimal(41.203339), decimal.Decimal(69.765714)],
        [decimal.Decimal(40.979924), decimal.Decimal(71.225837)],
        [decimal.Decimal(38.831461), decimal.Decimal(66.162693)],
        [decimal.Decimal(40.131718), decimal.Decimal(67.823338)],
        [decimal.Decimal(41.521693), decimal.Decimal(64.241037)],
        [decimal.Decimal(41.513229), decimal.Decimal(60.629134)],
        [decimal.Decimal(38.021292), decimal.Decimal(67.475130)]
    ];
    # Perhaps we can cache everything
    """
    if resource_name == "" and (region_id == "-1" or region_id == "") \
        and (status_id == "-1" or status_id == "")  \
        and (remainder_id == "-1" or remainder_id == "") \
        and (resource_kind == "-1" or resource_kind == "") \
        and numClusters == len(initial_centroids):

        query = "".join(
            ("SELECT json FROM cache WHERE region_id = -1 ",
            "AND area_id = -1 AND resource_kind = -1 ",
            "AND resource_group = -1 AND resource_type = -1 ",
            "AND resource_subtype = -1 AND numClusters = %s ",
            "AND status_id = -1 AND remainder_id = -1 AND role_id = %s"));
        g.cur.execute(query, [len(initial_centroids), role_id]);
        row = g.cur.fetchone();
        #print g.cur._last_executed
        if row:
            end_time = datetime.datetime.now();
            query_stats("/api/resources/", (end_time - start_time).total_seconds());
            return jsonify({
                "status": "success",
                "data": json.loads(row["json"]),
                "authenticated": (True if token else False)
            });
    if resource_name == "" and (region_id != "-1" and region_id != "") \
        and (area_id == "-1" or area_id == "") \
        and (status_id == "-1" or status_id == "")  \
        and (remainder_id == "-1" or remainder_id == "") \
        and (resource_kind == "-1" or resource_kind == ""):
        query = "".join(
            ("SELECT json FROM cache WHERE ",
            "region_id = %s ",
            "AND area_id = -1 AND resource_kind = -1 ",
            "AND resource_group = -1 AND resource_type = -1 ",
            "AND resource_subtype = -1 AND numClusters = 'All' ",
            "AND status_id = -1 AND remainder_id = -1 AND role_id = %s"));
        g.cur.execute(query, [region_id, role_id]);
        row = g.cur.fetchone();
        print g.cur._last_executed
        if row:
            print "Found match in the cache table"
            end_time = datetime.datetime.now();
            query_stats("/api/resources/", (end_time - start_time).total_seconds());
            return jsonify({
                "status": "success",
                "data": json.loads(row["json"]),
                "authenticated": (True if token else False)
            });
    """
    query = "".join((
        "SELECT dst.id, d.name_en AS deposit_name_en, d.name_ru  AS deposit_name_ru, " \
        "d.name_uz AS deposit_name_uz, a.name_en AS area_name_en, a.name_ru AS area_name_ru, " \
        "a.name_uz AS area_name_uz, a.name_en AS area_name_en, s.name_ru AS site_name_ru, " \
        "s.name_uz AS site_name_uz, s.name_en AS site_name_en, ds.latitude, ds.longitude, " \
        "(SELECT aa.name_ru FROM geomap.areas aa WHERE aa.region_id = a.region_id AND aa.area_id = 0) AS region_name_ru, " \
        "(SELECT aa.name_en FROM geomap.areas aa WHERE aa.region_id = a.region_id AND aa.area_id = 0) AS region_name_en, " \
        "(SELECT aa.name_uz FROM geomap.areas aa WHERE aa.region_id = a.region_id AND aa.area_id = 0) AS region_name_uz " \
        "FROM geomap.deposits_sites ds " \
        "INNER JOIN (SELECT dd.id, dd.name_ru, dd.name_uz, dd.name_en FROM geomap.deposits dd INNER JOIN geomap.permissions pp ON pp.resource_id = dd.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS d " \
        "ON ds.deposit_id = d.id " \
        "INNER JOIN (SELECT ss.id, ss.name_ru, ss.name_uz, ss.name_en FROM geomap.sites ss INNER JOIN geomap.permissions pp ON pp.resource_id = ss.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS s " \
        "ON ds.site_id = s.id " \
        "INNER JOIN (SELECT ddst.id, ddst.deposit_site_id, ddst.type_group_id, ddst.minerals_id, ddst.status_id, ddst.amount_a_b_c1, ddst.amount_c2 FROM geomap.deposits_sites_types ddst INNER JOIN geomap.permissions pp ON pp.resource_id = ddst.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS dst " \
        "ON ds.id = dst.deposit_site_id " \
        "INNER JOIN (SELECT dtdt.id, dtdt.kind_id, dtdt.group_id, dtdt.type_id, dtdt.subtype_id FROM geomap.deposit_types dtdt INNER JOIN geomap.permissions pp ON pp.resource_id = dtdt.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS dt " \
        "ON dt.id = dst.type_group_id " \
        "INNER JOIN (SELECT aa.id, aa.name_ru, aa.name_uz, aa.name_en, aa.region_id, aa.area_id FROM geomap.areas aa INNER JOIN geomap.permissions pp ON pp.resource_id = aa.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS a " \
        "ON a.id = ds.region_area_id " \
        "INNER JOIN permissions p ON p.resource_id = ds.resource_id " \
        "WHERE p.role_id = %s AND p.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read') "
    ));
    null = [params.append(role_id) for x in range(0, 6)];
    params.append("%" + resource_name + "%");
    if language != "":
        if language.lower() == "uz":
            query = "".join((query, "AND d.name_uz LIKE %s "));
        elif language.lower() == "en":
            query = "".join((query, "AND d.name_en LIKE %s "));
        else:
            query = "".join((query, "AND d.name_ru LIKE %s "));
    else:
        query = "".join((query, "AND d.name_ru LIKE %s "));

    if resource_kind != "" and resource_kind != "-1":
        if not re.match("^[1-9]{1}[0-9]*$", resource_kind):
            return jsonify({
                "status": "failure",
                "reason": "Неверный вид полезного ископаемого"
            });
        query = "".join((query,
                         "AND dt.kind_id = %s AND 0 < (SELECT COUNT(*) FROM deposit_types dtdt INNER JOIN permissions pp ON dtdt.resource_id = pp.resource_id WHERE dtdt.kind_id = %s AND dtdt.group_id = 0 AND dtdt.type_id = 0 AND dtdt.subtype_id = 0 AND pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) "));
        params.append(resource_kind);
        params.append(resource_kind);
        params.append(role_id);
        if resource_group != "" and resource_group != "-1":
            if not re.match("^[1-9]{1}[0-9]*$", resource_group):
                return jsonify({
                    "status": "failure",
                    "reason": "Неверная группа полезного ископаемого"
                });
            query = "".join((query,
                             "AND dt.group_id = %s AND 0 < (SELECT COUNT(*) FROM deposit_types dtdt INNER JOIN permissions pp ON dtdt.resource_id = pp.resource_id WHERE dtdt.kind_id = %s AND dtdt.group_id = %s AND dtdt.type_id = 0 AND dtdt.subtype_id = 0 AND pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) "))
            params.append(resource_group);
            params.append(resource_kind);
            params.append(resource_group);
            params.append(role_id);
            if resource_type != "" and resource_type != "-1":
                if not re.match("^[1-9]{1}[0-9]*$", resource_type):
                    return jsonify({
                        "status": "failure",
                        "reason": "Неверный тип полезного ископаемого"
                    });
                query = "".join((query,
                                 "AND dt.type_id = %s AND 0 < (SELECT COUNT(*) FROM deposit_types dtdt INNER JOIN permissions pp ON dtdt.resource_id = pp.resource_id WHERE dtdt.kind_id = %s AND dtdt.group_id = %s AND dtdt.type_id = %s AND dtdt.subtype_id = 0 AND pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) "))
                params.append(resource_type);
                params.append(resource_kind);
                params.append(resource_group);
                params.append(resource_type);
                params.append(role_id);
                if resource_subtype != "" and resource_subtype != "-1":
                    if not re.match("^[1-9]{1}[0-9]*$", resource_subtype):
                        return jsonify({
                            "status": "failure",
                            "reason": "Неверный подтип полезного ископаемого"
                        });
                    query = "".join((query, "AND dt.subtype_id = %s "))
                    params.append(resource_subtype);
            else:
                query = "".join((query,
                                 "AND 0 < (SELECT COUNT(*) FROM deposit_types dtdt INNER JOIN permissions pp ON dtdt.resource_id = pp.resource_id WHERE dtdt.kind_id = %s AND dtdt.group_id = %s AND pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) "))
                params.append(resource_kind);
                params.append(resource_group);
                params.append(role_id);
        else:
            query = "".join((query,
                             "AND 0 < (SELECT COUNT(*) FROM deposit_types dtdt INNER JOIN permissions pp ON dtdt.resource_id = pp.resource_id WHERE dtdt.kind_id = %s AND pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) "))
            params.append(resource_kind);
            params.append(role_id);
    else:
        query = "".join((query,
                         "AND 0 < (SELECT COUNT(*) FROM deposit_types dtdt INNER JOIN permissions pp ON dtdt.resource_id = pp.resource_id WHERE dtdt.kind_id <> 0 AND pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) "));
        params.append(role_id);

    if region_id != "" and region_id != "-1":
        if not re.match("^[1-9]{1}[0-9]*$", region_id):
            return jsonify({
                "status": "failure",
                "reason": "Неверная область"
            });
        query = "".join((query, "AND a.region_id = %s "))
        params.append(region_id);
        if area_id != "" and area_id != "-1":
            if not re.match("^[1-9]{1}[0-9]*$", area_id):
                return jsonify({
                    "status": "failure",
                    "reason": "Неверный район"
                });
            query = "".join((query, "AND a.area_id = %s "))
            params.append(area_id);
    if remainder_id != "" and remainder_id != "-1":
        if not re.match("^(1|2)$", remainder_id):
            return jsonify({
                "status": "failure",
                "reason": "Неверный идентификатор для остатка"
            });
        if remainder_id == "1":
            query = "".join((query, "AND (dst.amount_a_b_c1 > 0 OR dst.amount_c2 > 0) "))
        if remainder_id == "2":
            query = "".join((query, "AND dst.amount_a_b_c1 = 0 AND dst.amount_c2 = 0 "))
    if status_id != "" and status_id != "-1":
        if not re.match("^[1-9]{1}[0-9]*$", status_id):
            return jsonify({
                "status": "failure",
                "reason": "Неверный статус"
            });
        query = "".join((query, "AND dst.status_id = %s "));
        params.append(status_id);
    query = "".join((query, "ORDER BY deposit_name_ru"))
    g.cur.execute(query, params);
    print g.cur._last_executed
    result = [];
    X = [];
    Y = [];
    seen_ids = {};
    IDS = [];
    for row in g.cur.fetchall():
        X.append(decimal.Decimal(row["latitude"]));
        Y.append(decimal.Decimal(row["longitude"]));
        IDS.append(row["id"]);
        seen_ids[row["id"]] = {
            "ID": row["id"],
            "deposit_name_en": row["deposit_name_en"],
            "deposit_name_ru": row["deposit_name_ru"],
            "deposit_name_uz": row["deposit_name_uz"],
            "region_name_en": row["region_name_en"],
            "region_name_ru": row["region_name_ru"],
            "region_name_uz": row["region_name_uz"],
            "area_name_en": row["area_name_en"],
            "area_name_ru": row["area_name_ru"],
            "area_name_uz": row["area_name_uz"],
            "site_name_en": row["site_name_en"],
            "site_name_ru": row["site_name_ru"],
            "site_name_uz": row["site_name_uz"],
            "location": {
                "lat": float(row["latitude"]),
                "lng": float(row["longitude"]),
                # "coordinate_x": float(row["coordinate_x"]),
                # "coordinate_y": float(row["coordinate_y"]),
                # "zone": int(row["zone"])
            }
        }
    clustering = KMeansClustering();
    clusters = {};
    centroids = {};

    if numClusters == "All":
        numClusters = len(X);
    if len(X) < numClusters:
        numClusters = len(X);
    """
    if len(X) > 0:
        #if numClusters == len(initial_centroids):
        #	X=np.array(list(zip(X,Y)), dtype=np.dtype(decimal.Decimal));
        #	out = clustering.clusterPredifinedCentroids(X, initial_centroids, numIterations);
        #else:
    """
    # out = clustering.clusterRandomCentroids(X, Y, numClusters, numIterations);
    out = clustering.clusterCommon(X, Y, IDS);
    index = 0;
    for id in IDS:
        seen_ids[id]["cluster"] = out["clusters"][index];
        seen_ids[id]["centroid"] = {
            "lat": float(out["centroids"][index][0]),
            "lng": float(out["centroids"][index][1])
        };
        result.append(seen_ids[id]);
        index += 1;
    """
    if resource_name == "" and (region_id == "-1" or region_id == "") \
        and (status_id == "-1" or status_id == "")  \
        and (remainder_id == "-1" or remainder_id == "") \
        and (resource_kind == "-1" or resource_kind == "") \
        and numClusters == len(initial_centroids):
        try:
            lock_tables(g.cur, ["cache"], "WRITE");
            query = "".join(
                ("SELECT json FROM cache WHERE region_id = -1 ",
                "AND area_id = -1 AND resource_kind = -1 ",
                "AND resource_group = -1 AND resource_type = -1 ",
                "AND resource_subtype = -1 AND numClusters = %s ",
                "AND status_id = -1 AND remainder_id = -1 AND role_id = %s"));
            g.cur.execute(query, [len(initial_centroids), role_id]);
            row = g.cur.fetchone();
            if not row:
                query = "INSERT INTO geomap.cache( \
                    region_id, \
                    area_id, \
                    resource_kind, \
                    resource_group, \
                    resource_type, \
                    resource_subtype, \
                    numClusters, \
                    status_id, \
                    remainder_id, \
                    role_id, \
                    json) VALUES(-1, -1, -1, -1, -1, -1, %s, -1, -1, %s, %s)";
                g.cur.execute(query, [len(initial_centroids), role_id, json.dumps(result)]);
                g.db.commit();
        finally:
            unlock_tables(g.cur);
    if resource_name == "" and (region_id != "-1" and region_id != "") \
        and (area_id == "-1" or area_id == "") \
        and (status_id == "-1" or status_id == "")  \
        and (remainder_id == "-1" or remainder_id == "") \
        and (resource_kind == "-1" or resource_kind == ""):
        try:
            lock_tables(g.cur, ["cache"], "WRITE");
            query = "".join(
                ("SELECT json FROM cache WHERE region_id = -1 ",
                "AND region_id = %s ",
                "AND area_id = -1 AND resource_kind = -1 ",
                "AND resource_group = -1 AND resource_type = -1 ",
                "AND resource_subtype = -1 AND numClusters = 'All' ",
                "AND status_id = -1 AND remainder_id = -1 AND role_id = %s"));
            g.cur.execute(query, [region_id, role_id]);
            row = g.cur.fetchone();
            if not row:
                query = "INSERT INTO geomap.cache( \
                    region_id, \
                    area_id, \
                    resource_kind, \
                    resource_group, \
                    resource_type, \
                    resource_subtype, \
                    numClusters, \
                    status_id, \
                    remainder_id, \
                    role_id, \
                    json) VALUES(%s, -1, -1, -1, -1, -1, 'All', -1, -1, %s, %s)";
                g.cur.execute(query, [region_id, role_id, json.dumps(result)]);
                g.db.commit();
        finally:
            unlock_tables(g.cur);
    """
    end_time = datetime.datetime.now();
    query_stats("/api/resources/", (end_time - start_time).total_seconds());
    return jsonify({
        "status": "success",
        "data": result,
        "authenticated": (True if token else False)
    });


@app.route("/api/resource/")
def get_resource():
    start_time = datetime.datetime.now();
    resource_id = request.args.get("resource_id") or "";
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if authorize("/api/resource/", token, "read", remote_ip, remote_port) != True:
        register_authorization_failure("/api/resource/", token)
        return jsonify({"status": "failure", "reason": "forbidden"});
    role_id = get_role_for_token(token, remote_ip);
    if not re.match("^[1-9]{1}[0-9]*$", resource_id):
        return jsonify({
            "status": "failure",
            "reason": "Неверное полезное ископаемое"
        });
    query = "".join((
        "SELECT dst.id, d.name_en AS deposit_name_en, d.name_ru AS deposit_name_ru, ",
        "d.name_uz AS deposit_name_uz, a.name_en AS area_name_en, a.name_ru AS area_name_ru, ",
        "a.name_uz AS area_name_uz, a.name_en AS area_name_en, s.name_ru AS site_name_ru, ",
        "s.name_uz AS site_name_uz, s.name_en AS site_name_en, ds.latitude, ds.longitude, ",
        "m.name_ru AS mineral_name_ru, ",
        "m.name_en AS mineral_name_en, m.name_uz AS mineral_name_uz, ",
        "st.name_ru AS status_name_ru, st.name_en AS status_name_en, ",
        "st.name_uz AS status_name_uz, ",
        "au.name_ru AS amount_unit_ru, au.name_en AS amount_unit_en, ",
        "au.name_uz AS amount_unit_uz, ",
        "dst.amount_a_b_c1, dst.amount_c2, ",
        "dst.description, ",
        "(SELECT IF((SELECT COUNT(dc.id) FROM deposit_site_contours dc INNER JOIN permissions pp ON pp.resource_id = dc.resource_id WHERE dc.deposit_site_type_id=dst.id AND pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) > 0, 1, NULL)) AS deposit_locations, ",
        "(SELECT IF((SELECT COUNT(ii.id) FROM images ii WHERE ii.id=ds.image_cut_id AND ii.name <> 'Нет графики.jpg') > 0, ds.image_cut_id, NULL)) AS image_cut_id, ",
        "(SELECT IF((SELECT COUNT(ii.id) FROM images ii WHERE ii.id=ds.image_plan_id AND ii.name <> 'Нет графики.jpg') > 0, ds.image_plan_id, NULL)) AS image_plan_id, ",
        "(SELECT dtdt.name_ru FROM geomap.deposit_types dtdt WHERE dtdt.kind_id = dt.kind_id AND dtdt.group_id = 0 AND dtdt.type_id = 0 AND dtdt.subtype_id = 0) AS kind_name_ru, ",
        "(SELECT dtdt.name_en FROM geomap.deposit_types dtdt WHERE dtdt.kind_id = dt.kind_id AND dtdt.group_id = 0 AND dtdt.type_id = 0 AND dtdt.subtype_id = 0) AS kind_name_en, ",
        "(SELECT dtdt.name_uz FROM geomap.deposit_types dtdt WHERE dtdt.kind_id = dt.kind_id AND dtdt.group_id = 0 AND dtdt.type_id = 0 AND dtdt.subtype_id = 0) AS kind_name_uz, ",
        "(SELECT dtdt.name_ru FROM geomap.deposit_types dtdt WHERE dtdt.kind_id = dt.kind_id AND dtdt.group_id = dt.group_id AND dtdt.type_id = 0 AND dtdt.subtype_id = 0) AS group_name_ru, ",
        "(SELECT dtdt.name_en FROM geomap.deposit_types dtdt WHERE dtdt.kind_id = dt.kind_id AND dtdt.group_id = dt.group_id AND dtdt.type_id = 0 AND dtdt.subtype_id = 0) AS group_name_en, ",
        "(SELECT dtdt.name_uz FROM geomap.deposit_types dtdt WHERE dtdt.kind_id = dt.kind_id AND dtdt.group_id = dt.group_id AND dtdt.type_id = 0 AND dtdt.subtype_id = 0) AS group_name_uz, ",
        "(SELECT dtdt.name_ru FROM geomap.deposit_types dtdt WHERE dtdt.kind_id = dt.kind_id AND dtdt.group_id = dt.group_id AND dtdt.type_id = dt.type_id AND dtdt.subtype_id = 0) AS type_name_ru, ",
        "(SELECT dtdt.name_en FROM geomap.deposit_types dtdt WHERE dtdt.kind_id = dt.kind_id AND dtdt.group_id = dt.group_id AND dtdt.type_id = dt.type_id AND dtdt.subtype_id = 0) AS type_name_en, ",
        "(SELECT dtdt.name_uz FROM geomap.deposit_types dtdt WHERE dtdt.kind_id = dt.kind_id AND dtdt.group_id = dt.group_id AND dtdt.type_id = dt.type_id AND dtdt.subtype_id = 0) AS type_name_uz, ",
        "(SELECT dtdt.name_ru FROM geomap.deposit_types dtdt WHERE dtdt.kind_id = dt.kind_id AND dtdt.group_id = dt.group_id AND dtdt.type_id = dt.type_id AND dtdt.subtype_id = dt.subtype_id) AS subtype_name_ru, ",
        "(SELECT dtdt.name_en FROM geomap.deposit_types dtdt WHERE dtdt.kind_id = dt.kind_id AND dtdt.group_id = dt.group_id AND dtdt.type_id = dt.type_id AND dtdt.subtype_id = dt.subtype_id) AS subtype_name_en, ",
        "(SELECT dtdt.name_uz FROM geomap.deposit_types dtdt WHERE dtdt.kind_id = dt.kind_id AND dtdt.group_id = dt.group_id AND dtdt.type_id = dt.type_id AND dtdt.subtype_id = dt.subtype_id) AS subtype_name_uz, ",
        "(SELECT aa.name_ru FROM geomap.areas aa WHERE aa.region_id = a.region_id AND aa.area_id = 0) AS region_name_ru, ",
        "(SELECT aa.name_en FROM geomap.areas aa WHERE aa.region_id = a.region_id AND aa.area_id = 0) AS region_name_en, ",
        "(SELECT aa.name_uz FROM geomap.areas aa WHERE aa.region_id = a.region_id AND aa.area_id = 0) AS region_name_uz ",
        "FROM geomap.deposits_sites_types dst ",
        "INNER JOIN (SELECT dds.id, dds.region_area_id, dds.deposit_id, dds.site_id, dds.latitude, dds.longitude, dds.image_cut_id, dds.image_plan_id FROM geomap.deposits_sites dds INNER JOIN geomap.permissions pp ON pp.resource_id = dds.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS ds ",
        "ON dst.deposit_site_id = ds.id ",
        "INNER JOIN (SELECT dd.id, dd.name_en, dd.name_ru, dd.name_uz FROM geomap.deposits dd INNER JOIN geomap.permissions pp ON pp.resource_id = dd.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) as d ",
        "ON d.id = ds.deposit_id ",
        "INNER JOIN (SELECT ss.id, ss.name_ru, ss.name_uz, ss.name_en FROM geomap.sites ss INNER JOIN geomap.permissions pp ON pp.resource_id = ss.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS s ",
        "ON s.id = ds.site_id ",
        "INNER JOIN (SELECT aa.id, aa.name_ru, aa.name_uz, aa.name_en, aa.region_id FROM geomap.areas aa INNER JOIN geomap.permissions pp ON pp.resource_id = aa.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS a ",
        "ON a.id = ds.region_area_id ",
        "INNER JOIN (SELECT dtdt.id, dtdt.kind_id, dtdt.group_id, dtdt.type_id, dtdt.subtype_id FROM geomap.deposit_types dtdt INNER JOIN geomap.permissions pp ON pp.resource_id = dtdt.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS dt ",
        "ON dt.id = dst.type_group_id ",
        "INNER JOIN (SELECT mm.id, mm.name_ru, mm.name_uz, mm.name_en, mm.amount_unit_id FROM geomap.minerals mm INNER JOIN geomap.permissions pp ON pp.resource_id = mm.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS m ",
        "ON m.id = dst.minerals_id ",
        "INNER JOIN (SELECT auau.id, auau.name_ru, auau.name_uz, auau.name_en FROM geomap.amount_units auau INNER JOIN geomap.permissions pp ON pp.resource_id = auau.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS au ",
        "ON au.id = m.amount_unit_id ",
        "INNER JOIN (SELECT stst.id, stst.name_ru, stst.name_uz, stst.name_en FROM geomap.deposit_status stst INNER JOIN geomap.permissions pp ON pp.resource_id = stst.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS st ",
        "ON st.id = dst.status_id ",
        "INNER JOIN permissions p ON p.resource_id = dst.resource_id ",
        "WHERE p.role_id = %s AND p.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read') "
        "AND dst.id = %s"
    ));
    # print query
    params = [];
    [params.append(role_id) for x in range(0, 10)];
    params.append(resource_id);
    g.cur.execute(query, params);
    print g.cur._last_executed
    row = g.cur.fetchone();
    if not row:
        return jsonify({
            "status": "success",
            "data": {},
            "authenticated": (True if token else False)
        });
    end_time = datetime.datetime.now();
    query_stats("/api/resource/", (end_time - start_time).total_seconds());
    return jsonify({
        "status": "success",
        "data": {
            "ID": row["id"],
            "deposit_name_en": row["deposit_name_en"],
            "deposit_name_ru": row["deposit_name_ru"],
            "deposit_name_uz": row["deposit_name_uz"],
            "area_name_en": row["area_name_en"],
            "area_name_ru": row["area_name_ru"],
            "area_name_uz": row["area_name_uz"],
            "site_name_ru": row["site_name_ru"],
            "site_name_en": row["site_name_en"],
            "site_name_uz": row["site_name_uz"],
            "latitude": float(row["latitude"]),
            "longitude": float(row["longitude"]),
            # "coordinate_x"     : float(row["coordinate_x"]),
            # "coordinate_y"     : float(row["coordinate_y"]),
            # "zone"             : row["zone"],
            "mineral_name_ru": row["mineral_name_ru"],
            "mineral_name_en": row["mineral_name_en"],
            "mineral_name_uz": row["mineral_name_uz"],
            "status_name_ru": row["status_name_ru"],
            "status_name_en": row["status_name_en"],
            "region_name_ru": row["region_name_ru"],
            "region_name_en": row["region_name_en"],
            "region_name_uz": row["region_name_uz"],
            "description": row["description"],
            "kind_name_ru": row["kind_name_ru"],
            "kind_name_en": row["kind_name_en"],
            "kind_name_uz": row["kind_name_uz"],
            "group_name_ru": row["group_name_ru"],
            "group_name_en": row["group_name_en"],
            "group_name_uz": row["group_name_uz"],
            "type_name_ru": row["type_name_ru"],
            "type_name_en": row["type_name_en"],
            "type_name_uz": row["type_name_uz"],
            "subtype_name_ru": row["subtype_name_ru"],
            "subtype_name_en": row["subtype_name_en"],
            "subtype_name_uz": row["subtype_name_uz"],
            "amount_unit_ru": row["amount_unit_ru"],
            "amount_unit_en": row["amount_unit_en"],
            "amount_unit_uz": row["amount_unit_uz"],
            "image_cut_uuid": row["image_cut_id"],
            "image_plan_uuid": row["image_plan_id"],
            "amount_a_b_c1": float(row["amount_a_b_c1"]),
            "amount_c2": float(row["amount_c2"]),
            "deposit_locations": row["deposit_locations"]
        },
        "authenticated": (True if token else False)
    });


@app.route("/api/licenses/")
def get_resource_licenses():
    start_time = datetime.datetime.now();
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if authorize("/api/licenses/", token, "read", remote_ip, remote_port) != True:
        register_authorization_failure("/api/licenses/", token)
        return jsonify({"status": "failure", "reason": "forbidden"});
    role_id = get_role_for_token(token, remote_ip);
    resource_id = request.args.get("resource_id") or "";
    if not re.match("^[1-9]{1}[0-9]*$", resource_id):
        return jsonify({
            "status": "failure",
            "reason": "Неверное полезное ископаемое"
        });
    query = "".join((
        "SELECT dst.id, l.license, l.date_of_issue, ",
        "c.name_ru AS company_name_ru, ",
        "c.name_uz AS company_name_uz, ",
        "c.name_en AS company_name_en, ",
        "dsl.amount_a_b_c1, dsl.amount_c2 ",
        "FROM deposits_sites_licenses dsl ",
        "INNER JOIN (SELECT ll.id, ll.date_of_issue, ll.license, ll.company_id FROM geomap.licenses ll INNER JOIN geomap.permissions pp ON pp.resource_id = ll.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS l "
        "ON l.id = dsl.license_id ",
        "INNER JOIN (SELECT cc.id, cc.name_ru, cc.name_en, cc.name_uz FROM geomap.companies cc INNER JOIN geomap.permissions pp ON pp.resource_id = cc.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS c "
        "ON c.id = l.company_id ",
        "INNER JOIN (SELECT dstdst.id FROM geomap.deposits_sites_types dstdst INNER JOIN geomap.permissions pp ON pp.resource_id = dstdst.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS dst "
        "ON dst.id = dsl.deposit_site_type_id ",
        "INNER JOIN permissions p ON p.resource_id = dsl.resource_id ",
        "WHERE p.role_id = %s AND p.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read') "
        "AND dst.id = %s "
    ));
    params = [];
    [params.append(role_id) for x in range(0, 4)];
    params.append(resource_id);
    g.cur.execute(query, params);
    print(g.cur._last_executed);
    # print g.cur._last_executed;
    results = [];
    for row in g.cur.fetchall():
        results.append({
            "id": row["id"],
            "license": row["license"],
            "date_of_issue": row["date_of_issue"].strftime("%Y-%m-%d") if row["date_of_issue"] else None,
            "company_name_ru": row["company_name_ru"],
            "company_name_en": row["company_name_en"],
            "company_name_uz": row["company_name_uz"],
            "amount_a_b_c1": float(row["amount_a_b_c1"]),
            "amount_c2": float(row["amount_c2"])
        });
    end_time = datetime.datetime.now();
    query_stats("/api/licenses/", (end_time - start_time).total_seconds());
    return jsonify({
        "status": "success",
        "data": results,
        "authenticated": (True if token else False)
    });


@app.route("/api/resource_kinds/")
def get_list_of_resource_kinds():
    start_time = datetime.datetime.now();
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if authorize("/api/resource_kinds/", token, "read", remote_ip, remote_port) != True:
        register_authorization_failure("/api/resource_kinds/", token)
        return jsonify({"status": "failure", "reason": "forbidden"});
    role_id = get_role_for_token(token, remote_ip);
    query = "".join((
        "SELECT dt.kind_id, dt.name_ru, ",
        "dt.name_en, dt.name_uz ",
        "FROM deposit_types dt ",
        "INNER JOIN permissions p ON p.resource_id = dt.resource_id ",
        "WHERE p.role_id = %s AND p.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read') ",
        "AND dt.kind_id != 0 AND dt.group_id = 0 AND dt.type_id = 0 AND dt.subtype_id = 0"
    ));
    g.cur.execute(query, [role_id]);
    result = [{"kind_id": -1, "kind_name_ru": "Все", "kind_name_en": "All", "kind_name_uz": ""}];
    for row in g.cur.fetchall():
        result.append({
            "kind_id": row["kind_id"],
            "kind_name_en": row["name_en"],
            "kind_name_ru": row["name_ru"],
            "kind_name_uz": row["name_uz"]
        });
    end_time = datetime.datetime.now();
    query_stats("/api/resource_kinds/", (end_time - start_time).total_seconds());
    return jsonify({
        "status": "success",
        "data": result,
        "authenticated": (True if token else False)
    });


@app.route("/api/resource_groups/")
def get_list_of_resource_groups():
    start_time = datetime.datetime.now();
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if authorize("/api/resource_groups/", token, "read", remote_ip, remote_port) != True:
        register_authorization_failure("/api/resource_groups/", token)
        return jsonify({"status": "failure", "reason": "forbidden"});
    role_id = get_role_for_token(token, remote_ip);
    kind_id = request.args.get("kind_id") or "";
    query = "".join((
        "SELECT dt.group_id, dt.name_ru, ",
        "dt.name_en, dt.name_uz ",
        "FROM deposit_types dt ",
        "INNER JOIN permissions p ON p.resource_id = dt.resource_id ",
        "WHERE p.role_id = %s AND p.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read') ",
        "AND dt.kind_id = %s AND dt.group_id != 0 AND dt.type_id = 0 AND dt.subtype_id = 0 "
    ));
    result = [{"group_id": -1, "group_name_ru": "Все", "group_name_en": "All", "group_name_uz": ""}];
    if kind_id == "" or kind_id == "-1":
        return jsonify({
            "status": "success",
            "data": result,
            "authenticated": (True if token else False)
        });
    if not re.match("^[1-9]{1}[0-9]*$", kind_id):
        return jsonify({
            "status": "failure",
            "reason": "Неверный вид полезного ископаемого"
        });
    g.cur.execute(query, [role_id, kind_id]);
    for row in g.cur.fetchall():
        result.append({
            "group_id": row["group_id"],
            "group_name_en": row["name_en"],
            "group_name_ru": row["name_ru"],
            "group_name_uz": row["name_uz"]
        });
    end_time = datetime.datetime.now();
    query_stats("/api/resource_groups/", (end_time - start_time).total_seconds());
    return jsonify({
        "status": "success",
        "data": result,
        "authenticated": (True if token else False)
    });


@app.route("/api/resource_types/")
def get_list_of_resource_types():
    start_time = datetime.datetime.now();
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if authorize("/api/resource_types/", token, "read", remote_ip, remote_port) != True:
        register_authorization_failure("/api/resource_types/", token)
        return jsonify({"status": "failure", "reason": "forbidden"});
    role_id = get_role_for_token(token, remote_ip);
    kind_id = request.args.get("kind_id") or "";
    group_id = request.args.get("group_id") or "";
    query = "".join((
        "SELECT dt.type_id, dt.name_ru, ",
        "dt.name_en, dt.name_uz ",
        "FROM deposit_types dt ",
        "INNER JOIN permissions p ON p.resource_id = dt.resource_id ",
        "WHERE p.role_id = %s AND p.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read') ",
        "AND dt.kind_id = %s AND dt.group_id = %s AND dt.type_id != 0 AND dt.subtype_id = 0"
    ));
    result = [{"type_id": -1, "type_name_ru": "Все", "type_name_en": "All", "type_name_uz": ""}];
    if kind_id == "" or group_id == "":
        return jsonify({
            "status": "success",
            "data": result,
            "authenticated": (True if token else False)
        });
    if not re.match("^[1-9]{1}[0-9]*$", kind_id):
        return jsonify({
            "status": "failure",
            "reason": "Неверный вид полезного ископаемого"
        });
    if not re.match("^[1-9]{1}[0-9]*$", group_id):
        return jsonify({
            "status": "failure",
            "reason": "Неверная группа полезного ископаемого"
        });
    g.cur.execute(query, (role_id, kind_id, group_id));
    for row in g.cur.fetchall():
        result.append({
            "type_id": row["type_id"],
            "type_name_en": row["name_en"],
            "type_name_ru": row["name_ru"],
            "type_name_uz": row["name_uz"]
        });
    end_time = datetime.datetime.now();
    query_stats("/api/resource_types/", (end_time - start_time).total_seconds());
    return jsonify({
        "status": "success",
        "data": result,
        "authenticated": (True if token else False)
    });


@app.route("/api/resource_subtypes/")
def get_list_of_resource_subtypes():
    start_time = datetime.datetime.now();
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if authorize("/api/resource_subtypes/", token, "read", remote_ip, remote_port) != True:
        register_authorization_failure("/api/resource_subtypes/", token)
        return jsonify({"status": "failure", "reason": "forbidden"});
    role_id = get_role_for_token(token, remote_ip);
    kind_id = request.args.get("kind_id") or "";
    group_id = request.args.get("group_id") or "";
    type_id = request.args.get("type_id") or "";
    query = "".join((
        "SELECT dt.subtype_id, dt.name_ru, ",
        "dt.name_en, dt.name_uz ",
        "FROM deposit_types dt ",
        "INNER JOIN permissions p ON p.resource_id = dt.resource_id ",
        "WHERE p.role_id = %s AND p.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read') ",
        "AND dt.kind_id = %s AND dt.group_id = %s AND dt.type_id = %s AND dt.subtype_id != 0"
    ));
    result = [{"type_id": -1, "type_name_ru": "Все", "type_name_en": "All", "type_name_uz": ""}];
    if kind_id == "" or group_id == "" or type_id == "":
        return jsonify(result);
    if not re.match("^[1-9]{1}[0-9]*$", kind_id):
        return jsonify({
            "status": "failure",
            "reason": "Неверный вид полезного ископаемого"
        });
    if not re.match("^[1-9]{1}[0-9]*$", group_id):
        return jsonify({
            "status": "failure",
            "reason": "Неверная группа полезного ископаемого"
        });
    if not re.match("^[1-9]{1}[0-9]*$", type_id):
        return jsonify({
            "status": "failure",
            "reason": "Неверный тип полезного ископаемого"
        });
    g.cur.execute(query, (role_id, kind_id, group_id, type_id));
    for row in g.cur.fetchall():
        result.append({
            "subtype_id": row["subtype_id"],
            "type_name_en": row["name_en"],
            "type_name_ru": row["name_ru"],
            "type_name_uz": row["name_uz"]
        });
    end_time = datetime.datetime.now();
    query_stats("/api/resource_subtypes/", (end_time - start_time).total_seconds());
    return jsonify({
        "status": "success",
        "data": result,
        "authenticated": (True if token else False)
    });


@app.route("/api/print_report/")
def print_report():
    start_time = datetime.datetime.now();
    resource_id = request.args.get("resource_id") or "";
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if authorize("/api/print_report/", token, "read", remote_ip, remote_port) != True:
        register_authorization_failure("/api/print_report/", token);
        return jsonify({"status": "failure", "reason": "forbidden"});
    role_id = get_role_for_token(token, remote_ip);
    if not re.match("^[1-9]{1}[0-9]*$", resource_id):
        return jsonify({
            "status": "failure",
            "reason": "Неверное полезное ископаемое"
        });
    query = "".join((
        "SELECT dst.id, d.name_en AS deposit_name_en, d.name_ru  AS deposit_name_ru, ",
        "d.name_uz AS deposit_name_uz, a.name_en AS area_name_en, a.name_ru AS area_name_ru, ",
        "a.name_uz AS area_name_uz, a.name_en AS area_name_en, s.name_ru AS site_name_ru, ",
        "s.name_uz AS site_name_uz, s.name_en AS site_name_en, ds.latitude, ds.longitude, ",
        "m.name_ru AS mineral_name_ru, ",
        "m.name_en AS mineral_name_en, m.name_uz AS mineral_name_uz, ",
        "st.name_ru AS status_name_ru, st.name_en AS status_name_en, ",
        "st.name_uz AS status_name_uz, ",
        "au.name_ru AS amount_unit_ru, au.name_en AS amount_unit_en, ",
        "au.name_uz AS amount_unit_uz, ",
        "dst.description, ds.image_cut_id, ds.image_plan_id, ",
        "dst.amount_a_b_c1, dst.amount_c2, ",
        "(SELECT dtdt.name_ru FROM geomap.deposit_types dtdt WHERE dtdt.kind_id = dt.kind_id AND dtdt.group_id = 0 AND dtdt.type_id = 0 AND dtdt.subtype_id = 0) AS kind_name_ru, ",
        "(SELECT dtdt.name_en FROM geomap.deposit_types dtdt WHERE dtdt.kind_id = dt.kind_id AND dtdt.group_id = 0 AND dtdt.type_id = 0 AND dtdt.subtype_id = 0) AS kind_name_en, ",
        "(SELECT dtdt.name_uz FROM geomap.deposit_types dtdt WHERE dtdt.kind_id = dt.kind_id AND dtdt.group_id = 0 AND dtdt.type_id = 0 AND dtdt.subtype_id = 0) AS kind_name_uz, ",
        "(SELECT dtdt.name_ru FROM geomap.deposit_types dtdt WHERE dtdt.kind_id = dt.kind_id AND dtdt.group_id = dt.group_id AND dtdt.type_id = 0 AND dtdt.subtype_id = 0) AS group_name_ru, ",
        "(SELECT dtdt.name_en FROM geomap.deposit_types dtdt WHERE dtdt.kind_id = dt.kind_id AND dtdt.group_id = dt.group_id AND dtdt.type_id = 0 AND dtdt.subtype_id = 0) AS group_name_en, ",
        "(SELECT dtdt.name_uz FROM geomap.deposit_types dtdt WHERE dtdt.kind_id = dt.kind_id AND dtdt.group_id = dt.group_id AND dtdt.type_id = 0 AND dtdt.subtype_id = 0) AS group_name_uz, ",
        "(SELECT dtdt.name_ru FROM geomap.deposit_types dtdt WHERE dtdt.kind_id = dt.kind_id AND dtdt.group_id = dt.group_id AND dtdt.type_id = dt.type_id AND dtdt.subtype_id = 0) AS type_name_ru, ",
        "(SELECT dtdt.name_en FROM geomap.deposit_types dtdt WHERE dtdt.kind_id = dt.kind_id AND dtdt.group_id = dt.group_id AND dtdt.type_id = dt.type_id AND dtdt.subtype_id = 0) AS type_name_en, ",
        "(SELECT dtdt.name_uz FROM geomap.deposit_types dtdt WHERE dtdt.kind_id = dt.kind_id AND dtdt.group_id = dt.group_id AND dtdt.type_id = dt.type_id AND dtdt.subtype_id = 0) AS type_name_uz, ",
        "(SELECT dtdt.name_ru FROM geomap.deposit_types dtdt WHERE dtdt.kind_id = dt.kind_id AND dtdt.group_id = dt.group_id AND dtdt.type_id = dt.type_id AND dtdt.subtype_id = dt.subtype_id) AS subtype_name_ru, ",
        "(SELECT dtdt.name_en FROM geomap.deposit_types dtdt WHERE dtdt.kind_id = dt.kind_id AND dtdt.group_id = dt.group_id AND dtdt.type_id = dt.type_id AND dtdt.subtype_id = dt.subtype_id) AS subtype_name_en, ",
        "(SELECT dtdt.name_uz FROM geomap.deposit_types dtdt WHERE dtdt.kind_id = dt.kind_id AND dtdt.group_id = dt.group_id AND dtdt.type_id = dt.type_id AND dtdt.subtype_id = dt.subtype_id) AS subtype_name_uz, ",
        "(SELECT aa.name_ru FROM geomap.areas aa WHERE aa.region_id = a.region_id AND aa.area_id = 0) AS region_name_ru, ",
        "(SELECT aa.name_en FROM geomap.areas aa WHERE aa.region_id = a.region_id AND aa.area_id = 0) AS region_name_en, ",
        "(SELECT aa.name_uz FROM geomap.areas aa WHERE aa.region_id = a.region_id AND aa.area_id = 0) AS region_name_uz ",
        "FROM geomap.deposits_sites_types dst ",
        "INNER JOIN (SELECT dsds.id, dsds.site_id, dsds.deposit_id, dsds.region_area_id, dsds.latitude, dsds.longitude, dsds.image_cut_id, dsds.image_plan_id FROM geomap.deposits_sites dsds INNER JOIN geomap.permissions pp ON pp.resource_id = dsds.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS ds ",
        "ON dst.deposit_site_id = ds.id ",
        "INNER JOIN (SELECT aa.id, aa.name_ru, aa.name_uz, aa.name_en, aa.region_id FROM geomap.areas aa INNER JOIN geomap.permissions pp ON pp.resource_id = aa.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS a ",
        "ON a.id = ds.region_area_id ",
        "INNER JOIN (SELECT ss.id, ss.name_ru, ss.name_uz, ss.name_en FROM geomap.sites ss INNER JOIN geomap.permissions pp ON pp.resource_id = ss.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS s ",
        "ON s.id = ds.site_id ",
        "INNER JOIN (SELECT dd.id, dd.name_ru, dd.name_uz, dd.name_en FROM geomap.deposits dd INNER JOIN geomap.permissions pp ON pp.resource_id = dd.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS d ",
        "ON d.id = ds.deposit_id ",
        "INNER JOIN (SELECT dtdt.id, dtdt.kind_id, dtdt.group_id, dtdt.type_id, dtdt.subtype_id FROM geomap.deposit_types dtdt INNER JOIN geomap.permissions pp ON pp.resource_id = dtdt.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS dt ",
        "ON dt.id = dst.type_group_id ",
        "INNER JOIN (SELECT mm.id, mm.name_ru, mm.name_uz, mm.name_en, mm.amount_unit_id FROM geomap.minerals mm INNER JOIN geomap.permissions pp ON pp.resource_id = mm.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS m ",
        "ON m.id = dst.minerals_id ",
        "INNER JOIN (SELECT auau.id, auau.name_ru, auau.name_uz, auau.name_en FROM geomap.amount_units auau INNER JOIN geomap.permissions pp ON pp.resource_id = auau.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS au ",
        "ON au.id = m.amount_unit_id ",
        "INNER JOIN (SELECT stst.id, stst.name_ru, stst.name_uz, stst.name_en FROM geomap.deposit_status stst INNER JOIN geomap.permissions pp ON pp.resource_id = stst.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS st ",
        "ON st.id = dst.status_id ",
        "INNER JOIN permissions p ON p.resource_id = dst.resource_id ",
        "WHERE p.role_id = %s AND p.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read') ",
        "AND dst.id = %s"
    ));
    params = [];
    null = [params.append(role_id) for x in range(0, 9)];
    params.append(resource_id);
    g.cur.execute(query, params);
    # print g.cur._last_executed
    row = g.cur.fetchone();
    if not row:
        return jsonify({
            "status": "failure",
            "reason": "forbidden"
        }
        );
    resource = {
        "ID": row["id"],
        "deposit_name_en": row["deposit_name_en"],
        "deposit_name_ru": row["deposit_name_ru"],
        "deposit_name_uz": row["deposit_name_uz"],
        "area_name_en": row["area_name_en"],
        "area_name_ru": row["area_name_ru"],
        "area_name_uz": row["area_name_uz"],
        "site_name_ru": row["site_name_ru"],
        "site_name_en": row["site_name_en"],
        "site_name_uz": row["site_name_uz"],
        "latitude": float(row["latitude"]),
        "longitude": float(row["longitude"]),
        "coordinate_x": float(0),
        "coordinate_y": float(0),
        "zone": 0,
        "mineral_name_ru": row["mineral_name_ru"],
        "mineral_name_en": row["mineral_name_en"],
        "mineral_name_uz": row["mineral_name_uz"],
        "status_name_ru": row["status_name_ru"],
        "status_name_en": row["status_name_en"],
        "region_name_ru": row["region_name_ru"],
        "region_name_en": row["region_name_en"],
        "region_name_uz": row["region_name_uz"],
        "description": row["description"],
        "kind_name_ru": row["kind_name_ru"],
        "kind_name_en": row["kind_name_en"],
        "kind_name_uz": row["kind_name_uz"],
        "group_name_ru": row["group_name_ru"],
        "group_name_en": row["group_name_en"],
        "group_name_uz": row["group_name_uz"],
        "type_name_ru": row["type_name_ru"],
        "type_name_en": row["type_name_en"],
        "type_name_uz": row["type_name_uz"],
        "subtype_name_ru": row["subtype_name_ru"],
        "subtype_name_en": row["subtype_name_en"],
        "subtype_name_uz": row["subtype_name_uz"],
        "amount_unit_ru": row["amount_unit_ru"],
        "amount_unit_en": row["amount_unit_en"],
        "amount_unit_uz": row["amount_unit_uz"],
        "image_cut_uuid": row["image_cut_id"],
        "image_plan_uuid": row["image_plan_id"],
        "amount_a_b_c1": row["amount_a_b_c1"],
        "amount_c2": row["amount_c2"]
    };
    query = "".join((
        "SELECT dst.id, l.license, l.date_of_issue, ",
        "c.name_ru AS company_name_ru, ",
        "c.name_uz AS company_name_uz, ",
        "c.name_en AS company_name_en, ",
        "dsl.amount_a_b_c1, dsl.amount_c2 ",
        "FROM deposits_sites_licenses dsl ",
        "INNER JOIN (SELECT ll.id, ll.date_of_issue, ll.license, ll.company_id FROM geomap.licenses ll INNER JOIN geomap.permissions pp ON pp.resource_id = ll.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS l ",
        "ON l.id = dsl.license_id ",
        "INNER JOIN (SELECT cc.id, cc.name_ru, cc.name_en, cc.name_uz FROM geomap.companies cc INNER JOIN geomap.permissions pp ON pp.resource_id = cc.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS c ",
        "ON c.id = l.company_id ",
        "INNER JOIN (SELECT dstdst.id FROM geomap.deposits_sites_types dstdst INNER JOIN geomap.permissions pp ON pp.resource_id = dstdst.resource_id WHERE pp.role_id = %s AND pp.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')) AS dst ",
        "ON dst.id = dsl.deposit_site_type_id ",
        "INNER JOIN permissions p ON p.resource_id = dsl.resource_id ",
        "WHERE p.role_id = %s AND p.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read') ",
        "AND dst.id = %s "
    ));
    params = [];
    null = [params.append(role_id) for x in range(0, 4)];
    params.append(resource_id);
    g.cur.execute(query, params);
    licenses = [];
    a_b_c1_remainder = resource["amount_a_b_c1"];
    c2_remainder = resource["amount_c2"];
    for row in g.cur.fetchall():
        licenses.append({
            "id": row["id"],
            "license": row["license"],
            "date_of_issue": row["date_of_issue"].strftime("%Y-%m-%d") if row["date_of_issue"] else "",
            "company_name_ru": row["company_name_ru"],
            "company_name_en": row["company_name_en"],
            "company_name_uz": row["company_name_uz"],
            "amount_a_b_c1": float(row["amount_a_b_c1"]),
            "amount_c2": float(row["amount_c2"])
        });
    # c2_remainder -= row["amount_c2"];
    # a_b_c1_remainder -= row["amount_a_b_c1"];
    query = """SELECT i.name, i.data FROM images i
		INNER JOIN permissions p ON p.resource_id = i.resource_id 
		WHERE p.role_id = %s AND p.access_right_id = (SELECT id FROM rights WHERE access_right LIKE 'read')
		AND i.id = %s
	"""

    g.cur.execute(query, [role_id, resource["image_cut_uuid"]]);
    row = g.cur.fetchone();
    image_cut_data = None
    if row:
        image_cut_data = (row["data"] if row["name"] != u"Нет графики.jpg" else None);
    g.cur.execute(query, [role_id, resource["image_plan_uuid"]]);
    row = g.cur.fetchone();
    image_plan_data = None
    if row:
        image_plan_data = (row["data"] if row["name"] != u"Нет графики.jpg" else None);
    html = u"""
		<html>
			<head>
			<meta charset="utf-8">
			</head>
			<body>
				<h3 style='text-align: center'>Отчет по запасам месторождения</h3>
	""";
    html += u"   <h3 style='text-align: center'>";
    html += resource["deposit_name_ru"];
    html += u"   </h3>";
    html += u"   <h5>Общие сведения</h5>";
    html += u"   <table style='font-size: 8pt'>";
    html += u"       <tr>";
    html += u"            <td>";
    html += u"                   Область, район: ";
    html += resource["region_name_ru"] + u", " + resource["area_name_ru"] + u" район";
    html += u"            <td>";
    html += u"       </tr>";
    html += u"       <tr>";
    html += u"            <td>";
    html += u"                   Координаты (широта, долгота): ";
    html += str(resource["latitude"]) + u", " + str(resource["longitude"]);
    html += u"            <td>";
    html += u"       </tr>";
    html += u"       <tr>";
    html += u"            <td>";
    html += u"                   Полезные ископаемые: ";
    html += resource["mineral_name_ru"];
    html += u"            <td>";
    html += u"       </tr>";
    html += u"       <tr>";
    html += u"            <td>";
    html += u"                   Отсаток A, B, C1 (" + resource["amount_unit_ru"] + u"): ";
    html += str(round(a_b_c1_remainder, 2));
    html += u"            <td>";
    html += u"       </tr>";
    html += u"       <tr>";
    html += u"            <td>";
    html += u"                   Отсаток C2 (" + resource["amount_unit_ru"] + u"): ";
    html += str(round(c2_remainder, 2));
    html += u"            <td>";
    html += u"       </tr>";
    html += u"       <tr>";
    html += u"            <td>";
    html += u"                   Описание: ";
    html += resource["description"];
    html += u"            <td>";
    html += u"       </tr>";
    html += u"   </table>";
    if len(licenses) > 0:
        html += u"   <h5>Лицензии</h5>";
        html += u"   <table style='font-size: 8pt'>";
        html += u"       <tr>";
        html += u"            <td>";
        html += u"                Номер";
        html += u"            <td>";
        html += u"            <td>";
        html += u"                Дата выдачи";
        html += u"            <td>";
        html += u"            <td>";
        html += u"                A, B, C1";
        html += u"            <td>";
        html += u"            <td>";
        html += u"                C2";
        html += u"            <td>";
        html += u"       </tr>";
        for license in licenses:
            html += u"       <tr>";
            html += u"            <td>";
            html += license["license"];
            html += u"            <td>";
            html += u"            <td>";
            html += license["date_of_issue"];
            html += u"            <td>";
            html += u"            <td>";
            html += str(license["amount_a_b_c1"]);
            html += u"            <td>";
            html += u"            <td>";
            html += str(license["amount_c2"]);
            html += u"            <td>";
            html += u"       </tr>";
        html += u"   </table>";
    if image_plan_data != None:
        html += u"   <h5>Геологическая карта</h5>";
        html += u"   <img src=\"data:image/jpeg;base64,";
        html += image_plan_data;
        html += u"\" style=\"width:600px;\"><br/>";
    if image_cut_data != None:
        html += u"   <h5>Схематический разрез</h5>";
        html += u"   <img src=\"data:image/jpeg;base64,";
        html += image_cut_data;
        html += u"\" style=\"width:600px;\"><br/>";
    html += u"""
			</body>
		</html>
	""";
    stream = HTML(string=html).write_pdf();
    end_time = datetime.datetime.now();
    query_stats("/api/print_report/", (end_time - start_time).total_seconds());
    return Response(stream, content_type="application/pdf")


@app.route("/api/get_deposit_contours/", methods=["GET"])
def get_deposit_contours():
    start_time = datetime.datetime.now();
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    deposit_site_id = request.args.get("deposit_site_id") or "";
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if authorize("/api/get_deposit_contours/", token, "read", remote_ip, remote_port) != True:
        register_authorization_failure("/api/get_deposit_contours/", token);
        return jsonify({"status": "failure", "reason": "forbidden"});
    role_id = get_role_for_token(token, remote_ip);
    query = """
		SELECT ds.deposit_id FROM deposits_sites ds INNER JOIN permissions p ON p.resource_id = ds.resource_id 
			WHERE ds.id = %s AND p.role_id = %s AND p.access_right_id = 
				(SELECT id FROM rights WHERE access_right = "read");
	""";
    g.cur.execute(query, [deposit_site_id, role_id]);
    row = g.cur.fetchone();
    if not row:
        return jsonify({
            "status": "failure",
            "reason": "Неверный идентификатор месторождения и участка",
            "authenticated": (True if token else False)
        });
    deposit_id = row["deposit_id"];
    query = "SELECT latitude, longitude, point_number FROM deposit_contours WHERE deposit_id = %s ORDER BY point_number;";
    g.cur.execute(query, [deposit_id]);
    rows = g.cur.fetchall();
    results = [];
    for row in rows:
        results.append({
            "lat": float(row["latitude"]),
            "lng": float(row["longitude"]),
            "point_number": row["point_number"]
        });
    end_time = datetime.datetime.now();
    query_stats("/api/get_deposit_contours/", (end_time - start_time).total_seconds());
    return jsonify({
        "status": "success",
        "data": results,
        "authenticated": (True if token else False)
    });


@app.route("/api/get_deposit_site_contour/", methods=["GET"])
def get_deposit_site_contour():
    start_time = datetime.datetime.now();
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    deposit_site_type_id = request.args.get("deposit_site_id") or "";
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if authorize("/api/get_deposit_site_contour/", token, "read", remote_ip, remote_port) != True:
        register_authorization_failure("/api/get_deposit_site_contour/", token);
        return jsonify({"status": "failure", "reason": "forbidden"});
    role_id = get_role_for_token(token, remote_ip);
    query = """
		SELECT ds.deposit_id FROM deposits_sites ds INNER JOIN permissions p ON p.resource_id = ds.resource_id 
		WHERE ds.id = %s AND p.role_id = %s AND p.access_right_id = (SELECT id FROM rights WHERE access_right = "read");
	""";
    g.cur.execute(query, [deposit_site_type_id, role_id]);
    row = g.cur.fetchone();
    if not row:
        return jsonify({
            "status": "failure",
            "reason": "Неверный идентификатор месторождения и участка",
            "authenticated": (True if token else False)
        });
    query = """
		SELECT dsc.latitude, dsc.longitude, dsc.point_number 
		FROM deposit_site_contours dsc  
		INNER JOIN permissions p ON p.resource_id = dsc.resource_id 
		WHERE dsc.deposit_site_type_id = %s AND p.role_id = %s AND p.access_right_id = (SELECT id FROM rights WHERE access_right = "read")
		ORDER BY dsc.point_number ASC
	""";
    g.cur.execute(query, [deposit_site_type_id, role_id]);
    rows = g.cur.fetchall();
    results = [];
    for row in rows:
        results.append({
            "lat": float(row["latitude"]),
            "lng": float(row["longitude"]),
            "point_number": row["point_number"]
        });
    end_time = datetime.datetime.now();
    query_stats("/api/get_deposit_site_contour/", (end_time - start_time).total_seconds());
    return jsonify({
        "status": "success",
        "data": results,
        "authenticated": (True if token else False)
    });


@app.route("/api/investments/", methods=["GET"])
def investments():
    start_time = datetime.datetime.now();
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if authorize("/api/investments/", token, "read", remote_ip, remote_port) != True:
        register_authorization_failure("/api/investments/", token)
        return jsonify({"status": "failure", "reason": "forbidden"});
    role_id = get_role_for_token(token, remote_ip);
    region_id = request.args.get("region_id") or "";
    area_id = request.args.get("area_id") or "";
    mineral_id = request.args.get("mineral_id") or "";
    object_name = request.args.get("object_name") or "";

    query = """
		SELECT i.id, d.name_ru AS deposit, s.name_ru AS site, 
			m.name_ru AS mineral, i.area_ha, ds.latitude, ds.longitude 
			FROM investments i 
			INNER JOIN deposits_sites ds ON ds.id = i.deposit_site_id 
			INNER JOIN minerals m ON m.id = i.mineral_id 
			INNER JOIN permissions p ON p.resource_id = i.resource_id 
			INNER JOIN deposits d ON d.id = ds.deposit_id 
			INNER JOIN sites s ON s.id = ds.site_id 
			INNER JOIN areas a ON a.id = ds.region_area_id
			WHERE p.role_id = %s 
	""";
    params = [role_id];

    if region_id != "-1" and region_id != "":
        query += " AND a.region_id = %s"
        params.append(region_id);
    if area_id != "-1" and area_id != "":
        query += " AND a.area_id = %s"
        params.append(area_id);
    if mineral_id != "-1" and mineral_id != "":
        query += " AND m.id = %s"
        params.append(mineral_id);
    object_name = "%" + object_name + "%";
    query += " AND d.name_ru LIKE %s";
    params.append(object_name);
    g.cur.execute(query, params);
    rows = g.cur.fetchall();
    result = [];

    for row in rows:
        result.append({
            "id": row["id"],
            "lat": float(row["latitude"]),
            "lng": float(row["longitude"])
        });

    end_time = datetime.datetime.now();
    query_stats("/api/investments/", (end_time - start_time).total_seconds());
    return jsonify({
        "status": "success",
        "data": result,
        "authenticated": (True if token else False)
    });


@app.route("/api/investment/", methods=["GET"])
def investment():
    start_time = datetime.datetime.now();
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if authorize("/api/investment/", token, "read", remote_ip, remote_port) != True:
        register_authorization_failure("/api/investment/", token)
        return jsonify({"status": "failure", "reason": "forbidden"});
    role_id = get_role_for_token(token, remote_ip);
    investment_id = request.args.get("investment_id") or "";

    query = """
		SELECT i.id, d.name_ru AS deposit, s.name_ru AS site, 
			m.name_ru AS mineral, i.area_ha, ds.latitude, ds.longitude,
			i.presentation_url_ru, i.description_url_ru,
			(SELECT aa.name_ru FROM areas aa WHERE aa.id = ds.region_area_id) AS area_name_ru,
			(SELECT aa.name_ru FROM areas aa WHERE aa.region_id = (SELECT aaa.region_id FROM areas aaa WHERE aaa.id = ds.region_area_id) AND aa.area_id = 0) AS region_name_ru
			FROM investments i 
			INNER JOIN deposits_sites ds ON ds.id = i.deposit_site_id 
			INNER JOIN minerals m ON m.id = i.mineral_id 
			INNER JOIN permissions p ON p.resource_id = i.resource_id 
			INNER JOIN deposits d ON d.id = ds.deposit_id 
			INNER JOIN sites s ON s.id = ds.site_id 
			INNER JOIN areas a ON a.id = ds.region_area_id
			WHERE p.role_id = %s AND i.id = %s
	""";
    params = [role_id, investment_id];
    g.cur.execute(query, params);
    row = g.cur.fetchone();

    result = {
        "id": row["id"],
        "lat": float(row["latitude"]),
        "lng": float(row["longitude"]),
        "area_ha": float(row["area_ha"]),
        "area_name_ru": row["area_name_ru"],
        "region_name_ru": row["region_name_ru"],
        "description_url": row["description_url_ru"],
        "presentation_url": row["presentation_url_ru"],
        "minral_name_ru": row["mineral"],
        "deposit_name_ru": row["deposit"],
        "site_name_ru": row["site"]
    };

    end_time = datetime.datetime.now();
    query_stats("/api/investment/", (end_time - start_time).total_seconds());
    return jsonify({
        "status": "success",
        "data": result,
        "authenticated": (True if token else False)
    });


@app.route("/api/file/<path:path>", methods=["GET"])
def file_from_path(path):
    start_time = datetime.datetime.now();
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    # if authorize("/api/info_graphics/", token, "read", remote_ip, remote_port) != True:
    #	register_authorization_failure("/api/info_graphics/", token)
    #	return jsonify({"status": "failure", "reason": "forbidden"});
    return send_from_directory(config["FILE_STORAGE_DIR"], path)


@app.route("/api/info_graphics/", methods=["GET"])
def info_graphics():
    start_time = datetime.datetime.now();
    cookie = request.cookies.get("token", None);
    token = Utils.get_token(cookie);
    remote_ip = request.headers["X-Forwarded-For"] if "X-Forwarded-For" in request.headers else request.remote_addr;
    remote_port = request.environ.get("REMOTE_PORT");
    if authorize("/api/info_graphics/", token, "read", remote_ip, remote_port) != True:
        register_authorization_failure("/api/info_graphics/", token)
        return jsonify({"status": "failure", "reason": "forbidden"});
    role_id = get_role_for_token(token, remote_ip);
    region_id = request.args.get("region_id") or "";
    area_id = request.args.get("area_id") or "";
    resource_kind = request.args.get("resource_kind") or "";
    resource_group = request.args.get("resource_group") or "";
    resource_type = request.args.get("resource_type") or "";
    query = """
		SELECT dst.id AS dst_id, dst.amount_a_b_c1 AS available_a_b_c1, dst.amount_c2 AS available_c2, 
			m.name_ru AS mineral, au.name_ru AS amount_unit, dsl.amount_a_b_c1 AS amount_a_b_c1, dsl.amount_c2 AS amount_c2, 
				l.license, l.date_of_issue, 
				(SELECT aaa.region_id FROM areas aaa WHERE aaa.id = ds.region_area_id) AS region_id,
				(SELECT aaa.area_id FROM areas aaa WHERE aaa.id = ds.region_area_id) AS area_id,
				(SELECT aa.name_ru FROM areas aa WHERE region_id = (SELECT aaa.region_id FROM areas aaa WHERE aaa.id = ds.region_area_id) AND aa.area_id = 0) AS region, 
				a.region_id, t.group_id, t.kind_id, t.type_id FROM deposits_sites_types dst INNER JOIN minerals m ON m.id=dst.minerals_id 
				INNER JOIN amount_units au ON au.id = m.amount_unit_id 
				INNER JOIN deposits_sites ds ON ds.id=dst.deposit_site_id 
				INNER JOIN deposits_sites_licenses dsl ON dsl.deposit_site_type_id = dst.id 
				INNER JOIN licenses l ON l.id = dsl.license_id 
				INNER JOIN areas AS a ON a.id = ds.region_area_id 
				INNER JOIN deposit_types t ON t.id = dst.type_group_id 
				WHERE l.license != ""  AND (dsl.amount_a_b_c1 <> 0 OR dsl.amount_c2 <> 0)
				ORDER BY dst_id
	""";
    g.cur.execute(query);
    rows = g.cur.fetchall();
    data = [];

    for row in rows:
        if region_id != "" and region_id != "-1":
            if int(region_id) != row["region_id"]:
                continue;
        if resource_kind != "" and resource_kind != "-1":
            if int(resource_kind) != row["kind_id"]:
                continue;
        if resource_group != "" and resource_group != "-1":
            if int(resource_group) != row["group_id"]:
                continue;
        if resource_type != "" and resource_type != "-1":
            if int(resource_type) != row["type_id"]:
                continue;

        if not row["date_of_issue"] or row["date_of_issue"] == "":
            continue;

        if not row["license"]:
            continue;

        data.append({
            "dst_id": row["dst_id"],
            "available_a_b_c1": row["available_a_b_c1"],
            "available_c2": row["available_c2"],
            "mineral": row["mineral"],
            "amount_unit": row["amount_unit"],
            "amount_a_b_c1": row["amount_a_b_c1"],
            "amount_c2": row["amount_c2"],
            "region": row["region"],
            "license": row["license"],
            "year": str(row["date_of_issue"].strftime("%Y"))
        });

    csv_data = u"dst_id;available_a_b_c1;available_c2;amount_a_b_c1;amount_c2;license;date_of_issue;region\n";
    for row in data:
        csv_data += \
            str(row["dst_id"]) + ";" + \
            str(row["available_a_b_c1"]) + ";" + \
            str(row["available_c2"]) + ";" + \
            str(row["amount_a_b_c1"]) + ";" + \
            str(row["amount_c2"]) + ";" + \
            row["license"] + ";" + \
            str(row["year"]) + ";" + \
            row["region"] + \
            "\n";

    # (i) Prepare the data in CSV format
    # (ii) Write to temporary file
    # (iii) Execute infographics R script
    # (iv) Read output image file and write it as response

    file = tempfile.mkstemp();
    fh = codecs.open(file[1] + "_1.csv", "w+", "utf-8");
    fh.write(csv_data);
    fh.close();

    query = """
		SELECT ds.id AS ds_id, 
				(SELECT aa.name_ru FROM areas aa WHERE region_id = (SELECT aaa.region_id FROM areas aaa WHERE aaa.id = ds.region_area_id) AND aa.area_id = 0) AS region
				FROM deposits_sites_types ds
				INNER JOIN deposits d ON d.id = ds.deposit_id
				INNER JOIN sites s ON s.id = ds.site_id
				INNER JOIN areas a ON a.id = ds.region_area_id
				ORDER BY ds_id
	""";
    g.cur.execute(query);
    rows = g.cur.fetchall();
    data = [];

    for row in rows:
        if region_id != "" and region_id != "-1":
            if int(region_id) != row["region_id"]:
                continue;
        data.append({
            "ds_id": row["ds_id"],
            "region": row["region"]
        });

    csv_data = u"ds_id;region\n";
    for row in data:
        csv_data += \
            str(row["ds_id"]) + ";" + \
            row["region"] + "\n";

    fh = codecs.open(file[1] + "_2.csv", "w+", "utf-8");
    fh.write(csv_data);
    fh.close();

    query = """
		SELECT d.name_ru AS deposit, s.name_ru AS site, dst.deposit_site_id, 
		MAX(dst.amount_a_b_c1) / (SUM(dsl.amount_a_b_c1) + MAX(dst.amount_a_b_c1)) AS available_a_b_c1, 
		MAX(dst.amount_c2) / (MAX(dst.amount_c2) + SUM(dsl.amount_c2)) AS available_c2 
		FROM deposits_sites_types dst LEFT JOIN deposits_sites_licenses dsl ON dst.id = dsl.deposit_site_type_id 
		INNER JOIN deposits_sites ds ON ds.id = dst.deposit_site_id 
		INNER JOIN deposits d ON d.id = ds.deposit_id 
		INNER JOIN sites s ON s.id = ds.site_id GROUP BY dst.deposit_site_id;
	"""

    g.cur.execute(query);
    rows = g.cur.fetchall();
    csv_data = u"available\n"
    for row in rows:
        available = row["available_a_b_c1"]
        if row["available_a_b_c1"] == None:
            available = 1.0;
        else:
            available = float(available)
        csv_data += \
            str(available) + \
            "\n";

    fh = codecs.open(file[1] + "_3.csv", "w+", "utf-8");
    fh.write(csv_data);
    fh.close()

    query = ""

    os.system("touch " + file[1] + ".html")
    os.system("R --slave --args " + file[1] + " < render.R");
    # imgkit.from_file(file[1] + ".html", file[1] + ".jpg");
    os.system("xvfb-run wkhtmltoimage " + file[1] + ".html " + file[1] + ".jpg")

    image = open(file[1] + ".jpg", "r").read()
    encoded = base64.b64encode(image)

    os.remove(file[1] + ".jpg");
    os.remove(file[1] + ".html");
    os.remove(file[1] + "_1.csv");
    os.remove(file[1] + "_2.csv");
    os.remove(file[1] + "_3.csv");
    os.remove(file[1]);

    end_time = datetime.datetime.now();
    query_stats("/api/info_graphics/", (end_time - start_time).total_seconds());
    return jsonify({
        "status": "success",
        "data": encoded,
        "authenticated": (True if token else False)
    });


if __name__ == "__main__":
    app.run(port=5001);
