# local_settings.py
#
# The local settings in local_settings.py are used when running the application
#  in development. In production, use environment variables.
#
# To use this file:
#  Run cp local_settings.example.py local_settings.py
#  Edit contents of local_settings.py
#
# Please do not commit your changes to this file! lo

# Get your Google API credentials by going here:
#  https://console.developers.google.com
#
# Enable street view, Maps Geocoding API, and Places API Web Service

# Used by Google geocoder and Street View:
GOOGLE_API_KEY = "YOUR API KEY HERE"

# Used by the Places autocomplete:
GOOGLE_BROWSER_API_KEY = "YOUR API KEY HERE"

# You can set this to 'arcgis' or 'google'
GEOCODER = "google"

# Optional: Sign up for an ArcGIS developer account:
#  https://developers.arcgis.com
ARCGIS_CLIENT_ID = "YOUR CLIENT ID HERE"
ARCGIS_CLIENT_SECRET = ""

# Used by project and proposal importers:
SOCRATA_APP_TOKEN = ""
SOCRATA_APP_SECRET = ""

# Used for sending email:
SENDGRID_API_KEY = ""
# This key is used as a soft verification that messages posted to the inbound
# mail endpoint originate from a trusted source. On SendGrid, you must
# configure the URL to include a 'key' query param matching this value:
# '?key=SENDGRIDPARSEKEY'
SENDGRID_PARSE_KEY = ""

SENDGRID_TEMPLATES = {
    # Dictionary of human readable names to SendGrid template ids:
}

# Used by Azure Text Analytics; later--maybe news search
BING_API_KEY = ""

# Used for finding businesses related to a proposal
FOURSQUARE_CLIENT = ""
FOURSQUARE_SECRET = ""

# Used to generate absolute URLS, e.g., for emails
SERVER_DOMAIN = "localhost:4000"

ADMINS = [("Jane Doe", "janedoe@example.com")]
