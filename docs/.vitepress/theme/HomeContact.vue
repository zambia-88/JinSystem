<template>
  <section class="home-contact" aria-label="联系方式">
    <div class="home-section-head">
      <h2 class="home-section-title">联系方式</h2>
      <span class="home-section-sub">Contact</span>
    </div>
    <p class="home-contact-note">
      欢迎就矿业、AI、投资与长期成长相关话题交流。二维码与社交链接可在
      <a :href="withBase('/about')">关于页</a> 补充配置。
    </p>
    <div class="home-contact-grid">
      <a class="home-contact-item" href="mailto:Jinsystem@gmail.com">
        <span class="home-contact-icon">✉</span>
        <span>Email</span>
        <small>Jinsystem@gmail.com</small>
      </a>
      <a
        class="home-contact-item"
        href="https://github.com/zambia-88"
        target="_blank"
        rel="noopener noreferrer"
      >
        <span class="home-contact-icon">⌘</span>
        <span>GitHub</span>
        <small>@zambia-88</small>
      </a>
      <div class="home-contact-item home-contact-item--placeholder">
        <span class="home-contact-icon">微</span>
        <span>微信 / 公众号</span>
        <small>即将开放</small>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { withBase } from "vitepress";
</script>
