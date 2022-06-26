from urllib.parse import urlencode

from .base import BaseModule


class crt(BaseModule):

    flags = ["subdomain-enum", "passive"]
    watched_events = ["DNS_NAME"]
    produced_events = ["DNS_NAME"]
    in_scope_only = True

    def setup(self):
        self.processed = set()
        self.cert_ids = set()
        return True

    def filter_event(self, event):
        # only include targets
        if "target" in event.tags:
            return True
        # or out-of-scope DNS names that resolve to in-scope IPs
        elif event not in self.scan.target:
            if hash(self.helpers.parent_domain(event.data)) not in self.processed:
                return True
        return False

    def handle_event(self, event):
        if "target" in event.tags:
            query = str(event.data).lower()
        else:
            query = self.helpers.parent_domain(event.data).lower()

        if hash(query) not in self.processed:
            self.processed.add(hash(query))
            for hostname in self.query(query):
                if not hostname == event:
                    self.emit_event(hostname, "DNS_NAME", event)

    def query(self, domain):
        params = {"q": domain, "output": "json"}
        base_url = "https://crt.sh?"
        url = f"{base_url}{urlencode(params)}"
        res = self.helpers.request(url)
        j = {}
        try:
            j = res.json()
        except Exception:
            import traceback

            self.warning("Error decoding JSON")
            self.debug(traceback.format_exc())
        for cert_info in j:
            if not type(cert_info) == dict:
                continue
            cert_id = cert_info.get("id")
            if cert_id:
                if hash(cert_id) not in self.cert_ids:
                    self.cert_ids.add(hash(cert_id))
                    domain = cert_info.get("name_value")
                    if domain:
                        for d in domain.splitlines():
                            yield d.lower().strip("*.")
