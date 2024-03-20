import json
import config
import datetime

d = []

def object_hook(obj):
    new_dic = dict()
    for o in obj:
        try:
            new_dic[str(o)] = datetime.datetime.fromisoformat(obj[o])
        except TypeError:
            new_dic[str(o)] = obj[o]
            pass
    return new_dic


def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

try:
    with open(config.JSON_PATH + '/ghost.json') as f:
        d = json.load(f, object_hook=object_hook)
except FileNotFoundError:
    pass


print(d)


def save():
    global d
    # print(d)
    with open(config.JSON_PATH + '/ghost.json', 'w') as f:
        json.dump(d, f, indent=2, default=date_handler)

def get_exist(key:str, value:str|int, data):
    l = list(filter(lambda item : item[key] == value, data))
    if len(l) > 0:
        return l[0]
    return {}


def new_guild(guild_id:int, role_id:int):
    global d
    del_guild(guild_id)
    server = get_exist('server_id', guild_id, d)
    if any(server):
        print("data | pass new guild setup")
        return
    
    server['server_id'] = guild_id
    server['settings'] = {'role_id': role_id}
    server['users'] = []
    
    d.append(server)
    save()

def del_guild(guild_id:int):
    global d
    if not any(d):
        return
    server = get_exist('server_id', guild_id, d)
    if not any(server):
        return
    d.remove(server)
    save()


def set_role_id(guild_id:int, role_id:int):
    global d
    server = get_exist('server_id', guild_id, d)
    if not any(server):
        return
    settings = server["settings"]
    settings["role_id"] = role_id
    save()


def new_member(guild_id:int, member_id:int):
    global d
    server = get_exist('server_id', guild_id, d)
    if not any(server):
        return
    member = {"id": member_id, 'update_at': datetime.datetime.now(), 'count': 0, "role": False}
    server['users'].append(member)
    save()

def update_member(guild_id:int, member_id:int):
    global d
    server = get_exist('server_id', guild_id, d)
    if not any(server):
        return
    
    user = get_exist('id', member_id, server['users'])
    if not any(user):
        new_member(guild_id, member_id)

    user['count']+=1
    user['update_at'] = datetime.datetime.now()
    save()


def check_active(guild_id:int, member_id:int):
    global d
    server = get_exist('server_id', guild_id, d)
    if not any(server):
        return False
    
    user = get_exist('id', member_id, server['users'])
    if not any(user):
        return False
    
    return (user['update_at'] + datetime.timedelta(seconds=config.GHOST_LIMIT)) >= datetime.datetime.now()


def get_role_id(guild_id:int):
    global d
    server = get_exist('server_id', guild_id, d)
    if not any(server):
        return None
    settings = server['settings']
    return settings['role_id']

def check_member_role(guild_id:int, member_id:int):
    global d
    server = get_exist('server_id', guild_id, d)
    if not any(server):
        return
    
    user = get_exist('id', member_id, server['users'])
    if not any(user):
        return False
    
    return user['role']


def add_member_role(guild_id:int, member_id:int):
    global d
    server = get_exist('server_id', guild_id, d)
    if not any(server):
        return
    
    user = get_exist('id', member_id, server['users'])
    user['role'] = True

    save()

def remove_member_role(guild_id:int, member_id:int):
    global d
    server = get_exist('server_id', guild_id, d)
    if not any(server):
        return
    
    user = get_exist('id', member_id, server['users'])
    user['role'] = False

    save()


def check_guild(guild_id:int):
    global d
    return any(get_exist('server_id', guild_id, d))

def check_member(guild_id:int, member_id:int):
    global d
    server = get_exist('server_id', guild_id, d)
    
    return any(get_exist('id', member_id, server['users']))