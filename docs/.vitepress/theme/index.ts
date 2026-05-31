import { h } from "vue";
import DefaultTheme from "vitepress/theme";
import PostGrid from "./PostGrid.vue";
import DocMedia from "./DocMedia.vue";
import MobileAboutLink from "./MobileAboutLink.vue";
import "./custom.css";

const Layout = DefaultTheme.Layout;

export default {
  extends: DefaultTheme,
  Layout: () =>
    h(Layout, null, {
      "home-hero-after": () => h(PostGrid),
      "doc-before": () => h(DocMedia),
      "nav-bar-content-after": () => h(MobileAboutLink),
    }),
};
