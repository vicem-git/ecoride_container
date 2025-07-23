def safe_close(app):
    try:
        if hasattr(app, "db_manager"):
            app.db_manager.close_all()
    except Exception as e:
        print(f"Failed to close database pool on exit: {str(e)}")
