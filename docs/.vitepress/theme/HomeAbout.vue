<template>
  <section class="home-about" aria-label="关于 Nicholas">
    <div class="home-section-head">
      <h2 class="home-section-title">关于我</h2>
      <span class="home-section-sub">About Nicholas</span>
    </div>
    <div class="home-about-grid">
      <div class="home-about-copy">
        <p class="home-about-lead">
          我是 <strong>Nicholas</strong>，JinSystem 创始人。
        </p>
        <p class="home-about-en">
          I am Nicholas, the founder of JinSystem.
        </p>
        <p>
          长期从事非洲矿业项目投资与运营管理，同时持续研究 AI 应用、财富认知与个人成长。
        </p>
        <p class="home-about-en">
          My focus spans African mining investment, AI applications, wealth
          building, and personal development.
        </p>
        <ul class="home-about-beliefs">
          <li>真正的成长来自长期积累</li>
          <li>真正的价值来自持续输出</li>
        </ul>
        <a :href="withBase('/about')" class="home-about-link">完整介绍 →</a>
      </div>
      <div class="home-about-focus">
        <h3>Core Focus</h3>
        <ul>
          <li><span>Mining</span> 矿业投资与资源开发</li>
          <li><span>AI</span> 人工智能与效率提升</li>
          <li><span>Investing</span> 财富认知与投资研究</li>
          <li><span>Growth</span> 长期主义与个人成长</li>
        </ul>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { withBase } from "vitepress";
</script>
