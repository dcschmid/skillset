# API reference — <service name>

Spec source: <openapi.yaml | framework routes | codegen — name it>. Version: <the version your validator supports; probe before claiming 3.x>.

## Authentication

<scheme copied from middleware/decorators; header format from real code>

## Endpoints

### <METHOD> /<path>

Purpose: <one line> · Handler: <file:line or route id>

| Parameter | In | Type | Required | Source |
|---|---|---|---|---|
| <name> | <path|query|body> | <type from code> | <yes/no> | <verified where> |

Responses (status codes as returned by code, including errors):

| Status | When | Shape |
|---|---|---|
| 200 | <condition> | <schema/field list from serializer> |
| <4xx/5xx> | <condition from handlers/tests> | <error shape> |

```
# request — copy from a test or run it; never invent payloads
<verified example>
```

Pagination / filtering / rate limits: <from code or "not implemented — do not document">.

## Changelog / deprecations

<only changes with a real commit or version behind them>
