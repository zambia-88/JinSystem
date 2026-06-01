<script setup lang="ts">
import { onMounted, onBeforeUnmount, watch, ref, computed, nextTick } from "vue";
import { useRoute, useData } from "vitepress";
import type { WalineInstance } from "@waline/client";

declare const __WALINE_SERVER__: string;

const route = useRoute();
const { isDark, frontmatter } = useData();
const root = ref<HTMLElement | null>(null);
const ready = ref(false);
let waline: WalineInstance | null = null;

const visible = computed(() => {
  if (frontmatter.value.layout === "home") return false;
  if (frontmatter.value.comment === false) return false;
  return true;
});

const configured =
  typeof __WALINE_SERVER__ !== "undefined" && Boolean(__WALINE_SERVER__);

async function mountWaline() {
  if (!configured || !root.value) return;

  const { init } = await import("@waline/client");
  await import("@waline/client/style");

  waline?.destroy();
  waline = init({
    el: root.value,
    serverURL: __WALINE_SERVER__,
    path: route.path,
    lang: "zh-CN",
    dark: "html.dark",
    login: "force",
    pageview: false,
    comment: true,
    emoji: false,
    search: false,
    meta: [],
    requiredMeta: [],
    locale: {
      placeholder:
        "与同路人交流认知与成长；留言经审核后展示，请文明发言。",
      login: "登录后留言",
      logout: "退出",
      admin: "管理",
      submit: "发送留言",
      reply: "回复",
      cancel: "取消",
    },
  });
}

onMounted(async () => {
  ready.value = true;
  await nextTick();
  mountWaline();
});

watch(
  () => route.path,
  (path) => {
    waline?.update({ path });
  },
);

watch(isDark, (dark) => {
  waline?.update({ dark: dark ? "dark" : "light" });
});

onBeforeUnmount(() => {
  waline?.destroy();
  waline = null;
});
</script>

<template>
  <div v-if="visible" class="jin-comments">
    <div class="jin-comments-head">
      <span class="jin-comments-label">留言</span>
      <p class="jin-comments-hint">
        与同路人交流认知与成长；留言经审核后展示，请文明发言。须登录后发布。
      </p>
    </div>
    <p v-if="!configured" class="jin-comments-pending">
      留言服务配置中，即将开放。
    </p>
    <div v-else-if="ready" ref="root" class="waline-root" />
  </div>
</template>
