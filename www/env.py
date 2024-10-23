import environ


env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False),
    DATA_DIR=(str, 'data'),
    OPENAI_KEY=(str, None),
    DATABASE_DEFAULT=(str, 'sqlite:///data/db.sqlite3'),
    ALLOWED_HOSTS=(list, ['127.0.0.1', 'localhost']),
)

# Lookup ../.env, then .env
try:
    with open('../.env') as file:
        environ.Env.read_env(file)
except FileNotFoundError:
    try:
        with open('.env') as file:
            environ.Env.read_env(file)
    except FileNotFoundError:
        pass
