import {
  json,
  readBody,
  readRepoJson,
  requireAuth,
  triggerDeploy,
  writeRepoJson,
} from "./_lib.js";

export default async function handler(req, res) {
  if (req.method !== "PATCH" && req.method !== "POST") {
    json(res, 405, { error: "Method not allowed" });
    return;
  }
  if (!requireAuth(req, res)) return;
  try {
    const { slug, public: isPublic, autoDeploy = true } = await readBody(req);
    if (!slug || typeof isPublic !== "boolean") {
      json(res, 400, { error: "需要 slug 与 public (boolean)" });
      return;
    }
    const permPath = process.env.GITHUB_PERMISSIONS_PATH || "permissions.json";
    const { content: permissions, sha } = await readRepoJson(permPath);
    const data = permissions || {
      version: 1,
      defaults: { excel: false, manual: true },
      entries: {},
    };
    data.entries = data.entries || {};
    data.entries[slug] = isPublic;
    data.updatedAt = new Date().toISOString();
    await writeRepoJson(permPath, data, sha);

    if (autoDeploy) {
      await triggerDeploy();
    }

    json(res, 200, { ok: true, slug, public: isPublic });
  } catch (e) {
    json(res, 500, { error: String(e.message || e) });
  }
}
