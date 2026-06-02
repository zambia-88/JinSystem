<script setup lang="ts">
import { computed } from "vue";
import { useRoute, withBase } from "vitepress";

const route = useRoute();

const aboutHref = withBase("/about");

const isActive = computed(() => {
  const path = route.path.replace(/\/$/, "") || "/";
  const about = aboutHref.replace(/\/$/, "") || "/";
  return path === about;
});
</script>

<template>
  <a
    class="mobile-about-link"
    :class="{ active: isActive }"
    :href="aboutHref"
    aria-label="关于 JinSystem"
  >
    关于
  </a>
</template>
