import { json, requireAuth, triggerDeploy } from "./_lib.js";

export default async function handler(req, res) {
  if (req.method !== "POST") {
    json(res, 405, { error: "Method not allowed" });
    return;
  }
  if (!requireAuth(req, res)) return;
  try {
    await triggerDeploy();
    json(res, 200, { ok: true, message: "已触发同步部署" });
  } catch (e) {
    json(res, 500, { error: String(e.message || e) });
  }
}
