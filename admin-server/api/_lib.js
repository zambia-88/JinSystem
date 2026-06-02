import crypto from "node:crypto";

const TOKEN_TTL_MS = 12 * 60 * 60 * 1000;

export function json(res, status, body) {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.end(JSON.stringify(body));
}

export function readBody(req) {
  return new Promise((resolve, reject) => {
    let data = "";
    req.on("data", (c) => (data += c));
    req.on("end", () => {
      try {
        resolve(data ? JSON.parse(data) : {});
      } catch (e) {
        reject(e);
      }
    });
    req.on("error", reject);
  });
}

function b64url(input) {
  return Buffer.from(input)
    .toString("base64")
    .replace(/=/g, "")
    .replace(/\+/g, "-")
    .replace(/\//g, "_");
}

function b64urlDecode(str) {
  const pad = str.length % 4 === 0 ? "" : "=".repeat(4 - (str.length % 4));
  const b64 = str.replace(/-/g, "+").replace(/_/g, "/") + pad;
  return Buffer.from(b64, "base64").toString("utf8");
}

export function signToken(payload) {
  const secret = process.env.ADMIN_SECRET || process.env.ADMIN_PASSWORD || "";
  const body = b64url(JSON.stringify({ ...payload, exp: Date.now() + TOKEN_TTL_MS }));
  const sig = crypto.createHmac("sha256", secret).update(body).digest("hex");
  return `${body}.${sig}`;
}

export function verifyToken(token) {
  if (!token) return null;
  const secret = process.env.ADMIN_SECRET || process.env.ADMIN_PASSWORD || "";
  const [body, sig] = token.replace(/^Bearer\s+/i, "").split(".");
  if (!body || !sig) return null;
  const expected = crypto.createHmac("sha256", secret).update(body).digest("hex");
  if (sig !== expected) return null;
  try {
    const payload = JSON.parse(b64urlDecode(body));
    if (payload.exp < Date.now()) return null;
    return payload;
  } catch {
    return null;
  }
}

export function requireAuth(req, res) {
  const auth = req.headers.authorization || "";
  const payload = verifyToken(auth);
  if (!payload) {
    json(res, 401, { error: "未登录或会话已过期" });
    return null;
  }
  return payload;
}

function repoConfig() {
  const token = process.env.GITHUB_TOKEN;
  const privateRepo = process.env.GITHUB_PRIVATE_REPO;
  const branch = process.env.GITHUB_BRANCH || "main";
  if (!token || !privateRepo) {
    return null;
  }
  return { token, privateRepo, branch };
}

async function ghApi(path, { method = "GET", body, token }) {
  const res = await fetch(`https://api.github.com${path}`, {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "Content-Type": "application/json",
      "User-Agent": "JinSystem-Admin",
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (res.status === 404) return null;
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`GitHub API ${res.status}: ${text}`);
  }
  if (res.status === 204) return {};
  return res.json();
}

export async function readRepoJson(filePath) {
  const cfg = repoConfig();
  if (!cfg) throw new Error("GITHUB_TOKEN 或 GITHUB_PRIVATE_REPO 未配置");
  const [owner, repo] = cfg.privateRepo.split("/");
  const data = await ghApi(
    `/repos/${owner}/${repo}/contents/${encodeURIComponent(filePath)}?ref=${cfg.branch}`,
    { token: cfg.token }
  );
  if (!data) return { content: null, sha: null };
  const text = Buffer.from(data.content, "base64").toString("utf8");
  return { content: JSON.parse(text), sha: data.sha };
}

export async function writeRepoJson(filePath, obj, sha) {
  const cfg = repoConfig();
  if (!cfg) throw new Error("GITHUB_TOKEN 或 GITHUB_PRIVATE_REPO 未配置");
  const [owner, repo] = cfg.privateRepo.split("/");
  const content = Buffer.from(JSON.stringify(obj, null, 2), "utf8").toString("base64");
  const body = { message: `admin: update ${filePath}`, content, branch: cfg.branch };
  if (sha) body.sha = sha;
  return ghApi(`/repos/${owner}/${repo}/contents/${encodeURIComponent(filePath)}`, {
    method: "PUT",
    body,
    token: cfg.token,
  });
}

export async function triggerDeploy() {
  const cfg = repoConfig();
  if (!cfg) throw new Error("GITHUB_TOKEN 或 GITHUB_PRIVATE_REPO 未配置");
  const [owner, repo] = cfg.privateRepo.split("/");
  const workflow = process.env.GITHUB_WORKFLOW_FILE || "sync-public.yml";
  return ghApi(`/repos/${owner}/${repo}/actions/workflows/${workflow}/dispatches`, {
    method: "POST",
    body: { ref: cfg.branch },
    token: cfg.token,
  });
}

export function mergeList(manifest, permissions) {
  const entries = manifest?.entries || [];
  const map = permissions?.entries || {};
  const defaults = permissions?.defaults || { excel: false, manual: true };
  return entries
    .map((e) => {
      let isPublic;
      if (Object.prototype.hasOwnProperty.call(map, e.slug)) {
        isPublic = Boolean(map[e.slug]);
      } else {
        isPublic = Boolean(defaults[e.type] ?? defaults.manual);
      }
      return {
        slug: e.slug,
        title: e.title,
        category: e.category,
        type: e.type,
        public: isPublic,
      };
    })
    .sort((a, b) => a.title.localeCompare(b.title, "zh-CN"));
}
