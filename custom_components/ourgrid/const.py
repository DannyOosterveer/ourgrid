"""Constants for the OurGrid integration."""

DOMAIN = "ourgrid"

# Fixed server URL — not user-configurable
BASE_URL = "https://ourgrid.openremote.app"

# Config entry keys
CONF_REALM = "realm"
CONF_CLIENT_ID = "client_id"
CONF_CLIENT_SECRET = "client_secret"
CONF_CHALLENGE_ASSET_ID = "challenge_asset_id"
CONF_METER_ASSET_ID = "meter_asset_id"

# Poll interval in seconds
DEFAULT_SCAN_INTERVAL = 30

# OpenRemote attribute names
ATTR_CHALLENGE_START = "challengeStart"
ATTR_CHALLENGE_END = "challengeEnd"
ATTR_CHALLENGE_POINTS_EXCHANGE_RATE = "challengePointsExchangeRate"
ATTR_CHALLENGE_STATUS = "challengeStatus"
ATTR_CHALLENGE_POWER_LIMIT = "challengePowerLimit"
ATTR_CHALLENGE_JOIN_BUTTON = "challengeJoinButton"
ATTR_POWER = "power"

# Points & earnings
ATTR_CHALLENGE_EARNINGS = "challengeEarnings"
ATTR_CHALLENGES_JOINED = "challengesJoined"
ATTR_TOTAL_POINTS = "totalPoints"
ATTR_CHALLENGE_POINTS_CURRENT = "challengePointsCurrent"
ATTR_CHALLENGE_POINTS = "challengePoints"
ATTR_PEAK_POINTS = "peakPoints"

# Connectivity (diagnostic)
ATTR_CONNECTION_QUALITY = "connectionQuality"
ATTR_CONNECTION_STATUS = "connectionStatus"
ATTR_WIFI_SIGNAL = "wifiSignal"
