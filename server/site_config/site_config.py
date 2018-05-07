class SiteConfig():
    # If set, Users in the Group will receive forwarded messages.
    group_name = None
    hostnames = []
    # Extra template context
    extra_context = {}
    js_config = {}
    name = ""
    region_name = ""

    query_defaults = {}

    @property
    def proposal_query_defaults(self):
        return self.query_defaults

    @property
    def hostname(self):
        return self.hostnames[0]

    @property
    def name(self):
        return self.__module__.rsplit(".", 1)[-1]

    @property
    def base_url(self):
        hostname = self.hostnames[0]
        return f"https://{hostname}"

    @property
    def logo_text(self):
        return self.name

    def validate_subscription_query(self, sub, query):
        """
        Apply site-specific restrictions to Subscription queries.
        """
        return query
