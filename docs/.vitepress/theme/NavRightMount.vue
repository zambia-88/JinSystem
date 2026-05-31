<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from "vue";
import { useRoute } from "vitepress";

const hostRef = ref<HTMLElement | null>(null);
const route = useRoute();

function syncRightGroup() {
  const host = hostRef.value;
  const body = document.querySelector(".VPNavBar .content-body");
  const search = document.querySelector<HTMLElement>(".VPNavBarSearch.search");
  const appearance = document.querySelector<HTMLElement>(
    ".VPNavBarAppearance.appearance"
  );
  const status = document.querySelector<HTMLElement>(".jin-status-outer");
  if (!host || !body || !search || !appearance || !status) return;

  if (window.innerWidth < 960) {
    if (status.parentElement === host) {
      body.insertBefore(status, body.firstChild);
    }
    const about = body.querySelector(".mobile-about-link");
    const hamburger = body.querySelector(".VPNavBarHamburger");
    const anchor = about ?? hamburger;
    if (search.parentElement === host && anchor) {
      body.insertBefore(search, anchor);
    }
    if (appearance.parentElement === host && anchor) {
      body.insertBefore(appearance, anchor);
    }
    host.hidden = true;
    return;
  }

  host.hidden = false;
  for (const el of [search, appearance, status]) {
    if (el.parentElement !== host) host.appendChild(el);
  }
}

let mo: MutationObserver | undefined;
let timer: ReturnType<typeof setInterval> | undefined;

onMounted(() => {
  syncRightGroup();
  timer = setInterval(syncRightGroup, 250);
  setTimeout(() => {
    if (timer) clearInterval(timer);
  }, 4000);
  mo = new MutationObserver(syncRightGroup);
  const nav = document.querySelector(".VPNav");
  if (nav) mo.observe(nav, { childList: true, subtree: true });
  window.addEventListener("resize", syncRightGroup);
});

onUnmounted(() => {
  mo?.disconnect();
  if (timer) clearInterval(timer);
  window.removeEventListener("resize", syncRightGroup);
});

watch(
  () => route.path,
  () => requestAnimationFrame(syncRightGroup)
);
</script>

<template>
  <div ref="hostRef" class="jin-nav-right" aria-label="搜索主题与时间" hidden />
</template>
