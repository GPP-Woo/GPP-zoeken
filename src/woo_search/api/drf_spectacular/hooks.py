def remove_invalid_url_defaults(result, generator, **kwargs):  # pragma: no cover
    """
    Fix ``URLField(default="")`` schema generation.

    An empty string does not satisfy the `format: uri` validation, and schema validation
    tools can trip on this.

    The majority of the code here is inspired by the built in postprocess_schema_enums
    hook.

    TODO: contribute upstream patch
    """
    schemas = result.get("components", {}).get("schemas", {})

    def iter_prop_containers(schema):
        match schema:
            case {"properties": props}:
                yield props
            case {"oneOf": nested} | {"allOf": nested} | {"anyOf": nested}:
                yield from iter_prop_containers(nested)
            case list():
                for item in schema:
                    yield from iter_prop_containers(item)
            case dict():
                for nested in schema.values():
                    yield from iter_prop_containers(nested)

    # find all string (with format uri) properties that have an invalid default
    for props in iter_prop_containers(schemas):
        for prop_schema in props.values():
            if prop_schema.get("type") == "array":
                prop_schema = prop_schema.get("items", {})

            # only consider string types
            match prop_schema:
                case {"type": "string"}:
                    pass
                case {"type": list() as types} if "string" in types:
                    pass
                case _:
                    continue

            match prop_schema:
                case {"format": "uri", "default": ""}:
                    del prop_schema["default"]
                case _:
                    continue

    return result
