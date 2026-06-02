import { json, readBody, signToken } from "./_lib.js";

export default async function handler(req, res) {
  if (req.method !== "POST") {
    json(res, 405, { error: "Method not allowed" });
    return;
  }
  try {
    const { password } = await readBody(req);
    const expected = process.env.ADMIN_PASSWORD || "";
    if (!expected || password !== expected) {
      json(res, 401, { error: "密码错误" });
      return;
    }
    json(res, 200, { token: signToken({ role: "admin" }) });
  } catch (e) {
    json(res, 500, { error: String(e.message || e) });
  }
}
