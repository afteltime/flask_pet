import hashlib


def generate_action_token(user_id, post_id, action, *args, **kwargs):
    token_string = f"{user_id}-{post_id}-{action}"
    return hashlib.sha256(token_string.encode()).hexdigest()