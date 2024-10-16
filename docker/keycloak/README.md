# Keycloak infrastructure

WOO Publications supports OpenID Connect as an authentication protocol. Keycloak is an example of an Identity Provider that supports OIDC.

We include a compose stack for development and testing/CI purposes. This is **NOT** suitable for
production usage.

## docker compose

Start a Keycloak instance in your local environment from the parent directory:

```bash
docker compose -f docker/docker-compose.keycloak.yml up -d
```

This brings up Keycloak, the admin interface is accessible at http://localhost:8080/. You can now
log in with the `admin`/`admin` credentials.

In order to allow access to Keycloak via the same hostname via the WOO Publications backend container and the browser, add the following entry to your `/etc/hosts` file:

```
127.0.0.1 keycloak.woo-search.local
```

## Testing

This realm is used in the integration tests. We re-record the network traffic periodically (using
VCR.py). The primary reason this setup exists, is for automated testing reasons.

### Test data

**Clients**

- Client ID: `test-userinfo-jwt`, secret `ktGlGUELd1FR7dTXc84L7dJzUTjCtw9S`

  Configured to return the user info as a JWT rather than JSON response.

- Client ID: `testid`, secret: `7DB3KUAAizYCcmZufpHRVOcD0TOkNO3I`

**Users**

- `admin` / `admin`, intended to create as django user (can be made staff). The email address is
  `admin@example.com`.

## Exporting the Realm

In short - exporting through the admin UI (rightfully) obfuscates client secrets and user
credentials. However, for reproducible builds/environments, we want to include this data in the
Realm export.

Ensure the service is up and running through docker-compose.

Ensure that UID `1000` can write to `./keycloak/import/`:

```bash
chmod o+rwx ./keycloak/import/
```

Then open another terminal and run:

```bash
docker-compose -f docker-compose.keycloak.yml exec keycloak \
   /opt/keycloak/bin/kc.sh \
   export \
   --file /opt/keycloak/data/import/test-realm.json \
   --realm test
```
