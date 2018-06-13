class SiteConfig():
    # If set, Users in the Group will receive forwarded messages.
    group_name = None
    # A list of virtual hostnames to which this configuration applies:
    hostnames = []
    # Extra template context for all views:
    extra_context = {}
    # Merged with the output of `js_config` below
    extra_js_config = {}
    # A human-friendly name for this site
    name = ""
    # The region for this config
    region_name = ""
    town_id = None

    query_defaults = {}

    contacts = [
        {"topic": "About a project", "name": "planning-board"},
        {"topic": "About the website/technical issue", "name": "cornerwise"},
        {"topic": "Other", "name": "webmaster"}
    ]

    module_name = __module__.rsplit(".", 1)[-1]

    @property
    def proposal_query_defaults(self):
        return self.query_defaults

    @property
    def proposal_query_overrides(self):
        return {}

    @property
    def importer_query(self):
        return {"region_name": self.region_name}

    @property
    def hostname(self):
        return self.hostnames[0]

    @property
    def base_url(self):
        hostname = self.hostnames[0]
        return f"https://{hostname}"

    @property
    def logo_text(self):
        return self.name

    @property
    def contacts_config(self):
        return [
            {"topic": c["topic"], "name": c["name"]}
            for c in self.contacts
        ]

    def contact_for_name(self, name):
        return next((c for c in self.contacts if c["name"] == name), None)


    @property
    def js_config(self):
        conf = {
            "sitename": self.name,
            "contacts": self.contacts_config,
            "refPointDefault": {"lat": self.center.y, "lng": self.center.x}
        }
        conf.update(self.extra_js_config)
        return conf

    def validate_subscription_query(self, sub, query):
        """
        Apply site-specific restrictions to Subscription queries.
        """
        return query
