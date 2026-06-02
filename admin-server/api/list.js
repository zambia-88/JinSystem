import {
  json,
  mergeList,
  readRepoJson,
  requireAuth,
} from "./_lib.js";

export default async function handler(req, res) {
  if (req.method !== "GET") {
    json(res, 405, { error: "Method not allowed" });
    return;
  }
  if (!requireAuth(req, res)) return;
  try {
    const manifestPath = process.env.GITHUB_MANIFEST_PATH || "content-manifest.json";
    const permPath = process.env.GITHUB_PERMISSIONS_PATH || "permissions.json";
    const { content: manifest } = await readRepoJson(manifestPath);
    const { content: permissions } = await readRepoJson(permPath);
    if (!manifest) {
      json(res, 503, {
        error: "私有仓库中尚无 content-manifest.json，请先完成 SETUP-PRIVATE-REPO.md 初始化",
      });
      return;
    }
    json(res, 200, {
      items: mergeList(manifest, permissions || { entries: {}, defaults: {} }),
      updatedAt: permissions?.updatedAt || null,
    });
  } catch (e) {
    json(res, 500, { error: String(e.message || e) });
  }
}
