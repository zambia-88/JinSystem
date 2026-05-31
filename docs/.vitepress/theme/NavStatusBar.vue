<script setup lang="ts">
import { Solar } from "lunar-javascript";
import {
  computed,
  nextTick,
  onMounted,
  onUnmounted,
  ref,
  watch,
} from "vue";
import { useData } from "vitepress";
import { fetchWeather, type WeatherInfo } from "./utils/weather";

type StatusBarConfig = {
  city?: string;
  latitude?: number;
  longitude?: number;
};

const WEEK = ["日", "一", "二", "三", "四", "五", "六"] as const;
const MOBILE_MARQUEE_MAX = 767;
const MARQUEE_PX_PER_SEC = 36;

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

const outerRef = ref<HTMLElement | null>(null);
const trackRef = ref<HTMLElement | null>(null);
const marquee = ref(false);

let clockTimer: ReturnType<typeof setInterval> | undefined;
let resizeObserver: ResizeObserver | undefined;

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

const statusCopies = computed(() => (marquee.value ? [0, 1] : [0]));

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

function syncMarquee() {
  const outer = outerRef.value;
  const track = trackRef.value;
  const bar = outer?.querySelector<HTMLElement>(".nav-status-bar");
  if (!outer || !bar) {
    marquee.value = false;
    return;
  }

  if (window.innerWidth > MOBILE_MARQUEE_MAX) {
    marquee.value = false;
    track?.style.removeProperty("--marquee-duration");
    track?.style.removeProperty("--marquee-shift");
    return;
  }

  const overflow = bar.scrollWidth > outer.clientWidth + 2;
  marquee.value = overflow;

  if (!overflow || !track) {
    track?.style.removeProperty("--marquee-duration");
    track?.style.removeProperty("--marquee-shift");
    return;
  }

  const loopWidth = bar.scrollWidth + 32;
  const duration = Math.max(14, loopWidth / MARQUEE_PX_PER_SEC);
  track.style.setProperty("--marquee-duration", `${duration}s`);
  track.style.setProperty("--marquee-shift", `${loopWidth}px`);
}

async function refreshMarquee() {
  await nextTick();
  syncMarquee();
}

onMounted(async () => {
  clockTimer = setInterval(() => {
    now.value = new Date();
  }, 1000);

  await refreshMarquee();
  window.addEventListener("resize", refreshMarquee);
  resizeObserver = new ResizeObserver(() => {
    refreshMarquee();
  });
  if (outerRef.value) resizeObserver.observe(outerRef.value);

  const { lat, lon, city } = await resolveLocation();
  await loadWeather(lat, lon, city);
  await refreshMarquee();

  setInterval(async () => {
    const loc = await resolveLocation();
    await loadWeather(loc.lat, loc.lon, loc.city);
  }, 30 * 60 * 1000);
});

onUnmounted(() => {
  if (clockTimer) clearInterval(clockTimer);
  window.removeEventListener("resize", refreshMarquee);
  resizeObserver?.disconnect();
});

watch([timeText, weatherLine, lunarText], () => {
  refreshMarquee();
});
</script>

<template>
  <div
    ref="outerRef"
    class="jin-status-outer"
    :class="{ 'is-marquee': marquee }"
  >
    <div class="nav-status-marquee">
      <div ref="trackRef" class="nav-status-track">
        <div
          v-for="copy in statusCopies"
          :key="copy"
          class="nav-status-bar"
          :aria-hidden="copy === 1 ? true : undefined"
          :aria-label="copy === 0 ? '时间日期与天气' : undefined"
        >
          <span class="nav-status-chip nav-status-time">{{ timeText }}</span>
          <span class="nav-status-sep nav-status-sep--time" aria-hidden="true" />
          <span class="nav-status-chip nav-status-solar">{{ solarText }}</span>
          <span class="nav-status-sep nav-status-sep--solar" aria-hidden="true" />
          <span class="nav-status-chip nav-status-week">{{ weekText }}</span>
          <span class="nav-status-sep nav-status-sep--lunar" aria-hidden="true" />
          <span class="nav-status-chip nav-status-lunar">{{ lunarText }}</span>
          <span class="nav-status-sep nav-status-sep--weather" aria-hidden="true" />
          <span
            class="nav-status-chip nav-status-weather"
            :title="weather.city"
          >
            {{ weatherLine }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
