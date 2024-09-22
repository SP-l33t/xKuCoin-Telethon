from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int
    API_HASH: str
    GLOBAL_CONFIG_PATH: str = "TG_FARM"

    SLEEP_TIME: list[int] = [3600, 4000]
    START_DELAY: int = 30
    RANDOM_TAPS_COUNT: list[int] = [40, 55]
    MIN_ENERGY: int = 10
    REF_ID: str = 'cm91dGU9JTJGdGFwLWdhbWUlM0ZpbnZpdGVyVXNlcklkJTNENTI1MjU2NTI2JTI2cmNvZGUlM0Q='

    SESSIONS_PER_PROXY: int = 1
    USE_PROXY_FROM_FILE: bool = False
    USE_PROXY_CHAIN: bool = False

    DEVICE_PARAMS: bool = False

    DEBUG_LOGGING: bool = False


settings = Settings()
