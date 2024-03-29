from .exceptions import UnknownSelectorError


class SubjectSelector:
    def __init__(self, data: dict) -> None:
        self._suffix = "Selector"
        self._selector_type = self._get_selector_type(data)
        self._match_labels = self._get_labels(data["labels"])

    def _get_selector_type(self, data: dict) -> str:
        entities = [
            "reserved:host",
            "reserved:remote-node",
            "reserved:world",
        ]
        if any(label in data.get("labels", []) for label in entities):
            return "node"
        elif "namespace" in data:
            return "endpoint"
        else:
            raise UnknownSelectorError("Data: {data}")

    def _get_labels(self, labels: list[str]) -> dict:
        allowed_labels = [
            "app",
            "io.cilium.k8s.policy.serviceaccount",
            "io.kubernetes.pod.namespace",
        ]
        selected_labels = {}
        if self._selector_type == "endpoint":
            for label in labels:
                if label.startswith("k8s:"):
                    key, value = label.split(":", 1)[1].split("=", 1)
                    if key not in allowed_labels:
                        continue
                    selected_labels[key] = value

        return selected_labels

    def to_dict(self) -> dict:
        return {
            f"{self._selector_type}{self._suffix}": {
                "matchLabels": self._match_labels,
            },
        }

    def __eq__(self, obj: "SubjectSelector") -> bool:
        return self._selector_type == obj._selector_type and self._match_labels == obj._match_labels

    def __hash__(self) -> int:
        return hash(f"{self._selector_type}{self._match_labels}")
