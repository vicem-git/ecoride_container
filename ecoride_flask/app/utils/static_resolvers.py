from flask import current_app


def static_id_resolver(category, target_id):
    ids = current_app.static_ids.get(category, {})
    for name, _id in ids.items():
        if str(target_id) == str(_id):
            return name
    return None


def static_name_resolver(category, target_name):
    ids = current_app.static_ids.get(category, {})
    return ids.get(target_name)
