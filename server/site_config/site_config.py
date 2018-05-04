class SiteConfig():
    hostnames = []
    extra_context = {}
    js_config = {}
    name = ""

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
