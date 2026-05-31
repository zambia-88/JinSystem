/** WMO 天气代码 → 中文（Open-Meteo） */
const WMO: Record<number, string> = {
  0: "晴",
  1: "少云",
  2: "多云",
  3: "阴",
  45: "雾",
  48: "雾",
  51: "小雨",
  53: "小雨",
  55: "小雨",
  61: "小雨",
  63: "中雨",
  65: "大雨",
  71: "小雪",
  73: "中雪",
  75: "大雪",
  80: "阵雨",
  81: "阵雨",
  82: "暴雨",
  95: "雷雨",
  96: "雷雨",
  99: "雷雨",
};

const ICON: Record<number, string> = {
  0: "☀",
  1: "🌤",
  2: "⛅",
  3: "☁",
  45: "🌫",
  48: "🌫",
  51: "🌦",
  53: "🌦",
  55: "🌦",
  61: "🌧",
  63: "🌧",
  65: "🌧",
  71: "🌨",
  73: "🌨",
  75: "🌨",
  80: "🌦",
  81: "🌦",
  82: "⛈",
  95: "⛈",
  96: "⛈",
  99: "⛈",
};

export type WeatherInfo = {
  temp: number | null;
  desc: string;
  icon: string;
  city: string;
};

export function wmoLabel(code: number): string {
  return WMO[code] ?? "—";
}

export function wmoIcon(code: number): string {
  return ICON[code] ?? "◌";
}

export async function fetchWeather(
  lat: number,
  lon: number,
  city: string
): Promise<WeatherInfo> {
  const url = new URL("https://api.open-meteo.com/v1/forecast");
  url.searchParams.set("latitude", String(lat));
  url.searchParams.set("longitude", String(lon));
  url.searchParams.set("current", "temperature_2m,weather_code");
  url.searchParams.set("timezone", "Asia/Shanghai");

  const res = await fetch(url.toString());
  if (!res.ok) throw new Error("weather fetch failed");

  const data = (await res.json()) as {
    current?: { temperature_2m?: number; weather_code?: number };
  };
  const code = data.current?.weather_code ?? 0;
  return {
    temp:
      data.current?.temperature_2m != null
        ? Math.round(data.current.temperature_2m)
        : null,
    desc: wmoLabel(code),
    icon: wmoIcon(code),
    city,
  };
}
