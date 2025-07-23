from flask_login import UserMixin


class SessionUser(UserMixin):
    def __init__(
        self,
        account_id,
        email,
        account_status_id,
        account_access_id,
        user_id=None,
        username=None,
    ):
        self.id = str(account_id)
        self.email = email
        self.account_status_id = str(account_status_id)
        self.account_access_id = str(account_access_id)
        self.user_id = str(user_id) if user_id is not None else None
        self.username = username

    @property
    def is_active(self):
        from flask import current_app

        active_status_id = current_app.static_ids["account_status"]["active"]
        return self.account_status_id == active_status_id

    def get_id(self):
        return self.id
