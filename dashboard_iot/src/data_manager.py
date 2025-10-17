"""
Utility helpers to load and mutate dashboard demo data.

The data layer is intentionally lightweight – it reads JSON fixtures from the
``data`` directory and exposes convenience helpers to translate the stored
values into percentages suitable for the dashboard widgets.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple
import json


@dataclass
class SensorReading:
    """In-memory representation of a sensor entry."""

    name: str
    value: float
    unit: str
    minimum: float
    maximum: float
    alert: float | None = None

    def as_percentage(self) -> float:
        """Return the current value scaled to 0-100 for circular gauges."""
        span = max(self.maximum - self.minimum, 1e-6)
        percentage = (self.value - self.minimum) / span * 100.0
        return max(0.0, min(100.0, percentage))

    def update_from_percentage(self, percentage: float) -> float:
        """
        Update the stored value given a 0-100 percentage slider and return it.
        """
        bounded = max(0.0, min(100.0, percentage))
        span = self.maximum - self.minimum
        if span <= 0:
            self.value = self.minimum
            return self.value
        self.value = self.minimum + (span * bounded / 100.0)
        return self.value


class DataManager:
    """
    Read dashboards fixtures and offer helpers for downstream widgets.
    """

    def __init__(self, base_path: Path) -> None:
        self.base_path = Path(base_path)
        self._devices: List[Dict[str, Any]] = []
        self._sensors: Dict[str, SensorReading] = {}
        self._activity: List[float] = []
        self._consumption: Dict[str, float] = {}

    # -- Loading ----------------------------------------------------------------
    def load(self) -> None:
        """Load devices and sensor fixtures from disk."""
        devices_path = self.base_path / "data" / "devices.json"
        sensors_path = self.base_path / "data" / "sensor_data.json"

        self._devices = self._read_json(devices_path, fallback=[])
        sensor_payload = self._read_json(sensors_path, fallback={})

        self._sensors = self._parse_sensor_payload(sensor_payload)
        self._activity = list(sensor_payload.get("actividad_horaria", []))
        self._consumption = dict(sensor_payload.get("consumo_dispositivos", {}))

    # -- Access helpers --------------------------------------------------------
    @property
    def devices(self) -> List[Dict[str, Any]]:
        return list(self._devices)

    def sensors(self) -> Iterable[SensorReading]:
        return list(self._sensors.values())

    def get_sensor(self, key: str) -> SensorReading | None:
        return self._sensors.get(key.lower())

    def set_sensor_percentage(self, key: str, percentage: float) -> float:
        """
        Update a sensor given a slider movement and return the new numeric value.
        """
        sensor = self.get_sensor(key)
        if sensor is None:
            raise KeyError(f"Unknown sensor '{key}'")
        return sensor.update_from_percentage(percentage)

    def get_sensor_percentage(self, key: str) -> float:
        sensor = self.get_sensor(key)
        if sensor is None:
            raise KeyError(f"Unknown sensor '{key}'")
        return sensor.as_percentage()

    def get_activity_series(self) -> List[float]:
        return list(self._activity)

    def get_consumption_items(self) -> List[Tuple[str, float]]:
        return list(self._consumption.items())

    # -- Internal utilities ----------------------------------------------------
    def _parse_sensor_payload(
        self, payload: Dict[str, Any]
    ) -> Dict[str, SensorReading]:
        readings: Dict[str, SensorReading] = {}
        for key, value in payload.items():
            if not isinstance(value, dict):
                continue
            if not {"valor", "unidad", "min", "max"} <= set(value):
                continue
            human_name = key.replace("_", " ").title()
            reading = SensorReading(
                name=human_name,
                value=float(value["valor"]),
                unit=str(value.get("unidad", "")),
                minimum=float(value.get("min", 0.0)),
                maximum=float(value.get("max", 100.0)),
                alert=float(value["alerta"]) if "alerta" in value else None,
            )
            readings[key.lower()] = reading
        return readings

    @staticmethod
    def _read_json(path: Path, fallback: Any) -> Any:
        try:
            with path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except FileNotFoundError:
            return fallback
