# Troubleshooting



## Debugging discipline

Most time lost in a long debugging session comes from skipping these.

- **Read the logs first.** Whatever the symptom is, the cause usually announces itself in the logs before you start guessing.

  ```
  docker compose logs <service> --tail 200
  docker compose logs <service> --tail 0 -f
  ```

## Removing provisioned resources

Provisioning is declarative when adding resources — define the YAML, the resource appears. It is **explicit** when removing them. Deleting the YAML alone does not delete the resource from the database, because provisioning has no concept of "this used to be declared and now isn't." You have to tell it.

The implementation differs by resource type because dashboards have a directory-watch model and datasources don't.

### Dashboards

With `disableDeletion: false` in your dashboards provider config, removing the JSON file from `./grafana/dashboards/` deletes the dashboard from the database on the next poll. The directory is watched; absence is removal.

With `disableDeletion: true`, file removal alone won't delete. Use an explicit cleanup file:

```yaml
# ./grafana/provisioning/dashboards/cleanup-foo.yaml
apiVersion: 1
deleteDashboards:
  - orgId: 1
    uid: <dashboard-uid>
```

### Datasources

No directory watch exists for datasources. To remove one, add a cleanup file:

```yaml
# ./grafana/provisioning/datasources/cleanup-foo.yaml
apiVersion: 1
deleteDatasources:
  - name: Foo
    orgId: 1
```

### Keep the cleanup file separate

Provisioning runs delete operations **before** create operations within a single boot. If `deleteDatasources` and `datasources:` blocks live in the same file, you delete the datasource on boot and immediately recreate it — every restart. The cleanup must live in its own file.

After the cleanup runs once and the resource is gone, delete the cleanup file. Leaving it is idempotent (deleting nothing is a no-op), but if you ever re-add the resource later it will get deleted again on every boot.

### The general principle

Any declarative-config tool has to choose how removal works. Tools that watch a directory (Kubernetes manifests) can infer removal from absence. Tools that read independent declarations (Grafana datasources, Ansible playbooks) cannot — they need explicit removal directives. When adopting a new declarative tool, find out which model it uses before you need to remove something.


## NAT hairpinning: when public URLs fail from inside the LAN

A specific topology trap: the resource you're trying to reach is on your LAN, but you're addressing it by its public hostname. The request leaves the LAN, hits your router's WAN side, and the router has to loop it back to the internal host. Many consumer and SMB routers don't support this (the feature is called NAT hairpinning or NAT loopback), so the connection fails or times out.

### Symptom

`https://service.example.com` works from a phone on cellular but fails from another machine on the same LAN.

### When the public URL is the right choice anyway

If the target service is *not* on your LAN — running on a different network, a different cloud, a colocation rack — the public URL is the only option, and TLS is appropriate because the traffic crosses the public internet. The principle below applies when you have a choice; for genuinely remote services, you don't.

### When to switch to a direct address

If the target service is reachable directly from where you're calling from, prefer that over the public URL. For example, with a Prometheus datasource:

```yaml
datasources:
  - name: Prometheus
    type: prometheus
    # Pick the URL form based on where Prometheus runs:
    #   - On the LAN (same network as the Docker host):  http://prometheus-local-ip-address:9090
    #   - Remote (different network):                    https://prometheus.domain.tld
    url: http://prometheus-local-ip-address:9090
```

### The principle

Internal traffic shouldn't leave the network just to come back. If the source and target are on the same LAN or Docker network, address the target directly. The public hostname exists for clients that can't reach the target any other way — usually external users — and using it from inside the LAN buys nothing but adds a round trip through the router, TLS overhead, and dependence on NAT hairpinning support.

Public URLs are for users. Direct addresses are for services on the same network. When source and target are on different networks, the public URL becomes the direct address — and that's the correct topology, not a workaround.
