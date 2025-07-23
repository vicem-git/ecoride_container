from app.models import SessionUser
from app.utils import login_manager


def session_user_loader(app):
    @login_manager.user_loader
    def user_loader(account_id):
        print("Loading user:", account_id)
        with app.db_manager.connection() as conn:
            conn.autocommit = True
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT a.id, a.email, a.account_status_id, a.account_access_id, u.id, u.username FROM accounts a LEFT JOIN users u ON u.account_id = a.id WHERE a.id = %s",
                    (account_id,),
                )
                row = cursor.fetchone()
                if not row:
                    return None

                (
                    account_id,
                    email,
                    account_status_id,
                    account_access_id,
                    user_id,
                    username,
                ) = row

                return SessionUser(
                    account_id=account_id,
                    email=email,
                    account_status_id=account_status_id,
                    account_access_id=account_access_id,
                    user_id=user_id,
                    username=username,
                )
