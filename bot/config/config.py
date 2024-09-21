from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int
    API_HASH: str
    GLOBAL_CONFIG_PATH: str = "TG_FARM"

    CLICKS: list[int] = [300, 1000]

    AUTO_UPGRADE_CLICKING_POWER: bool = False
    AUTO_UPGRADE_CLICKING_POWER_LEVEL: int = 20

    AUTO_UPGRADE_TIMER: bool = False
    AUTO_UPGRADE_TIMER_LEVEL: int = 20

    AUTO_UPGRADE_REDUCE_COOLDOWN: bool = True
    AUTO_UPGRADE_REDUCE_COOLDOWN_LEVEL: int = 20

    RANDOM_DELAY_IN_RUN: int = 30

    REF_ID: str = '525256526'

    SESSIONS_PER_PROXY: int = 1
    USE_PROXY_FROM_FILE: bool = False
    USE_PROXY_CHAIN: bool = False

    DEVICE_PARAMS: bool = False

    DEBUG_LOGGING: bool = False


settings = Settings()
