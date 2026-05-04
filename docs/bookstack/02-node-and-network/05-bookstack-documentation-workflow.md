# BookStack Documentation Workflow

BookStack is the living manual for the SMI machine project. Operators and maintainers can update pages as settings, troubleshooting steps, and evidence change.

## Login

Open:

```text
http://192.168.0.20:6875/login
```

Change the default admin password before relying on it.

## API

BookStack API access is configured on the node at:

```text
/srv/smi-ai/config/bookstack-api.env
```

The token is intentionally not shown in pages or stored in git.

## Recommended Use

- Document approved settings and changes.
- Add photos/screenshots from faults and changeovers.
- Keep vendor documents indexed.
- Use pages for procedures and fault history, not secrets.
