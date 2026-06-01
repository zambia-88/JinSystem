import { h } from "vue";
import DefaultTheme from "vitepress/theme";
import PostGrid from "./PostGrid.vue";
import HomePillars from "./HomePillars.vue";
import HomeStats from "./HomeStats.vue";
import HomeIntro from "./HomeIntro.vue";
import HomeFeatured from "./HomeFeatured.vue";
import HomeAbout from "./HomeAbout.vue";
import HomeContact from "./HomeContact.vue";
import DocMedia from "./DocMedia.vue";
import MobileAboutLink from "./MobileAboutLink.vue";
import NavStatusBar from "./NavStatusBar.vue";
import NavRightMount from "./NavRightMount.vue";
import "./custom.css";

const Layout = DefaultTheme.Layout;

export default {
  extends: DefaultTheme,
  Layout: () =>
    h(Layout, null, {
      "nav-bar-content-before": () => h(NavStatusBar),
      "nav-bar-content-after": () =>
        h("div", { style: "display:contents" }, [
          h(NavRightMount),
          h(MobileAboutLink),
        ]),
      "home-hero-after": () =>
        h("div", { class: "home-sections" }, [
          h(HomeIntro),
          h(HomeStats),
          h(HomePillars),
          h(HomeFeatured),
          h(PostGrid),
          h(HomeAbout),
          h(HomeContact),
        ]),
      "doc-before": () => h(DocMedia),
    }),
};
