# 赛博礼堂

一个可在浏览器中体验的 3D 礼佛空间，包含佛像、庭院、蒲团、上香和礼佛互动。

## 本地预览

在项目目录运行任意静态文件服务器，然后打开其显示的本地地址。GitHub Pages 发布后无需构建步骤。

## GitHub Pages

仓库推送到 `main` 分支后，GitHub Actions 会自动发布网站。确保仓库的 Pages 构建来源设为 **GitHub Actions**。

发布地址：<https://jellyiilu.github.io/cyber-temple/>

佛像模型位于 `assets/buddha.glb`。Three.js r128 和 GLTFLoader 随网站保存在 `assets/vendor/`，页面无需从第三方 CDN 加载运行时依赖。
