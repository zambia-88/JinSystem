<script setup lang="ts">
import { Solar } from "lunar-javascript";
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useData } from "vitepress";
import { fetchWeather, type WeatherInfo } from "./utils/weather";

type StatusBarConfig = {
  city?: string;
  latitude?: number;
  longitude?: number;
};

const WEEK = ["日", "一", "二", "三", "四", "五", "六"] as const;

const { theme } = useData();
const cfg = computed(
  () => (theme.value.statusBar ?? {}) as StatusBarConfig
);

const now = ref(new Date());
const weather = ref<WeatherInfo>({
  temp: null,
  desc: "—",
  icon: "◌",
  city: cfg.value.city ?? "本地",
});

let clockTimer: ReturnType<typeof setInterval> | undefined;

const timeText = computed(() => {
  const d = now.value;
  const h = String(d.getHours()).padStart(2, "0");
  const m = String(d.getMinutes()).padStart(2, "0");
  const s = String(d.getSeconds()).padStart(2, "0");
  return `${h}:${m}:${s}`;
});

const solarText = computed(() => {
  const d = now.value;
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`;
});

const weekText = computed(() => `星期${WEEK[now.value.getDay()]}`);

const lunarText = computed(() => {
  try {
    const lunar = Solar.fromDate(now.value).getLunar();
    return `农历${lunar.getMonthInChinese()}月${lunar.getDayInChinese()}`;
  } catch {
    return "";
  }
});

const weatherLine = computed(() => {
  const w = weather.value;
  if (w.temp == null) return `${w.icon} ${w.desc}`;
  return `${w.icon} ${w.desc} ${w.temp}°C`;
});

async function loadWeather(lat: number, lon: number, city: string) {
  try {
    weather.value = await fetchWeather(lat, lon, city);
  } catch {
    weather.value = { temp: null, desc: "—", icon: "◌", city };
  }
}

function resolveLocation(): Promise<{
  lat: number;
  lon: number;
  city: string;
}> {
  const fallback = {
    lat: cfg.value.latitude ?? 30.5928,
    lon: cfg.value.longitude ?? 114.3055,
    city: cfg.value.city ?? "武汉",
  };

  if (!import.meta.env.SSR && navigator.geolocation) {
    return new Promise((resolve) => {
      navigator.geolocation.getCurrentPosition(
        (pos) =>
          resolve({
            lat: pos.coords.latitude,
            lon: pos.coords.longitude,
            city: "本地",
          }),
        () => resolve(fallback),
        { timeout: 8000, maximumAge: 600_000 }
      );
    });
  }
  return Promise.resolve(fallback);
}

onMounted(async () => {
  clockTimer = setInterval(() => {
    now.value = new Date();
  }, 1000);

  const { lat, lon, city } = await resolveLocation();
  await loadWeather(lat, lon, city);

  setInterval(async () => {
    const loc = await resolveLocation();
    await loadWeather(loc.lat, loc.lon, loc.city);
  }, 30 * 60 * 1000);
});

onUnmounted(() => {
  if (clockTimer) clearInterval(clockTimer);
});
</script>

<template>
  <div class="jin-status-outer">
    <div class="nav-status-bar" aria-label="时间日期与天气">
      <div class="nav-status-line nav-status-line--primary">
        <span class="nav-status-chip nav-status-time">{{ timeText }}</span>
        <span class="nav-status-sep" aria-hidden="true" />
        <span class="nav-status-chip">{{ solarText }}</span>
        <span class="nav-status-sep nav-status-sep--week" aria-hidden="true" />
        <span class="nav-status-chip nav-status-week">{{ weekText }}</span>
      </div>
      <div class="nav-status-line nav-status-line--secondary">
        <span class="nav-status-chip nav-status-lunar">{{ lunarText }}</span>
        <span class="nav-status-sep" aria-hidden="true" />
        <span
          class="nav-status-chip nav-status-weather"
          :title="weather.city"
        >
          {{ weatherLine }}
        </span>
      </div>
    </div>
  </div>
</template>
