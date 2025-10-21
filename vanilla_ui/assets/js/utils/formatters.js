const pad = (value) => value.toString().padStart(2, "0");

export const formatDate = (isoString) => {
  if (!isoString) {
    return "Fecha desconocida";
  }
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) {
    return "Fecha desconocida";
  }
  return date.toLocaleDateString("es-ES", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
};

export const formatDuration = (seconds) => {
  if (!Number.isFinite(seconds) || seconds <= 0) {
    return "00:00";
  }
  const totalSeconds = Math.round(seconds);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const secs = totalSeconds % 60;
  if (hours > 0) {
    return `${hours}:${pad(minutes)}:${pad(secs)}`;
  }
  return `${pad(minutes)}:${pad(secs)}`;
};

export const truncateText = (text, length = 120) => {
  if (!text) {
    return "";
  }
  return text.length > length ? `${text.slice(0, length)}…` : text;
};
