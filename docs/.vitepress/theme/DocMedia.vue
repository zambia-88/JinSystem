<script setup lang="ts">
import { computed } from "vue";
import { useData, withBase } from "vitepress";

const { frontmatter } = useData();

const cover = computed(() => {
  const c = frontmatter.value.cover as string | undefined;
  if (!c) return "";
  return c.startsWith("http") ? c : withBase(c);
});

const mediaUrl = computed(() => {
  const u = frontmatter.value.mediaUrl as string | undefined;
  if (!u) return "";
  return u.startsWith("http") ? u : withBase(u);
});

const mediaType = computed(
  () => (frontmatter.value.mediaType as string) || ""
);

const hasMedia = computed(
  () => cover.value || (mediaUrl.value && mediaType.value)
);
</script>

<template>
  <div v-if="hasMedia" class="doc-media">
    <img
      v-if="cover && mediaType !== 'video' && mediaType !== 'audio'"
      :src="cover"
      :alt="(frontmatter.title as string) || ''"
      class="doc-cover"
    />
    <img
      v-else-if="cover && (mediaType === 'video' || mediaType === 'audio')"
      :src="cover"
      :alt="(frontmatter.title as string) || ''"
      class="doc-cover doc-cover-poster"
    />
    <video
      v-if="mediaType === 'video' && mediaUrl"
      class="doc-video"
      controls
      playsinline
      :poster="cover || undefined"
    >
      <source :src="mediaUrl" />
    </video>
    <audio
      v-if="mediaType === 'audio' && mediaUrl"
      class="doc-audio"
      controls
      :src="mediaUrl"
    />
  </div>
</template>
