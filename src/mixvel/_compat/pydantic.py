from __future__ import annotations

from typing import Any, Callable, Dict

try:  # pragma: no cover - prefer the real dependency when available
    from pydantic import BaseModel, ConfigDict, Field  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - lightweight fallback for offline envs
    class ConfigDict(dict):
        def __init__(self, **kwargs: Any) -> None:
            super().__init__(**kwargs)

    class _Missing:
        pass

    _MISSING = _Missing()

    class FieldInfo:
        __slots__ = ("default", "default_factory")

        def __init__(self, default: Any = _MISSING, default_factory: Callable[[], Any] | None = None) -> None:
            self.default = default
            self.default_factory = default_factory

    def Field(*, default: Any = _MISSING, default_factory: Callable[[], Any] | None = None) -> FieldInfo:
        return FieldInfo(default=default, default_factory=default_factory)

    class BaseModelMeta(type):
        def __new__(mcls, name: str, bases: tuple[type, ...], namespace: Dict[str, Any], **kwargs: Any) -> type:
            annotations = namespace.get("__annotations__", {})
            field_infos: Dict[str, FieldInfo] = {}
            for base in bases:
                base_fields = getattr(base, "_field_infos", None)
                if base_fields:
                    field_infos.update(base_fields)
            for field_name in annotations:
                value = namespace.get(field_name, _MISSING)
                if isinstance(value, FieldInfo):
                    field_infos[field_name] = value
                    namespace.pop(field_name)
                elif value is not _MISSING:
                    field_infos[field_name] = FieldInfo(default=value)
                elif field_name not in field_infos:
                    field_infos[field_name] = FieldInfo()
            namespace["_field_infos"] = field_infos
            return super().__new__(mcls, name, bases, namespace)

    class BaseModel(metaclass=BaseModelMeta):
        model_config = ConfigDict()

        def __init__(self, **data: Any) -> None:
            consumed = set()
            for field_name, info in self._field_infos.items():  # type: ignore[attr-defined]
                if field_name in data:
                    value = data[field_name]
                    consumed.add(field_name)
                else:
                    if info.default_factory is not None:
                        value = info.default_factory()
                    elif info.default is not _MISSING:
                        value = info.default
                    else:
                        raise TypeError(f"Missing field '{field_name}' for {self.__class__.__name__}")
                setattr(self, field_name, value)
            extra = set(data.keys()) - consumed
            if extra:
                extras = ", ".join(sorted(extra))
                raise TypeError(f"Unexpected fields for {self.__class__.__name__}: {extras}")

        def model_dump(self) -> Dict[str, Any]:
            return {name: getattr(self, name) for name in self._field_infos.keys()}  # type: ignore[attr-defined]
