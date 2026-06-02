import { createReadStream, existsSync } from "node:fs";
import { extname, join, normalize } from "node:path";
import { createServer } from "node:http";
import { fileURLToPath } from "node:url";
import { dirname } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const publicDir = join(__dirname, "public");
const srcDir = join(__dirname, "src");
const port = Number(process.env.FRONTEND_PORT || 5173);

const mimeTypes = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg"
};

function resolveFile(urlPath) {
  if (urlPath === "/" || urlPath === "") {
    return join(publicDir, "index.html");
  }
  const cleanPath = normalize(decodeURIComponent(urlPath)).replace(/^(\.\.[/\\])+/, "");
  if (cleanPath.startsWith("/src/")) {
    return join(srcDir, cleanPath.replace(/^\/src\//, ""));
  }
  return join(publicDir, cleanPath.replace(/^\/+/, ""));
}

createServer((request, response) => {
  const url = new URL(request.url || "/", `http://${request.headers.host}`);
  const filePath = resolveFile(url.pathname);
  const finalPath = existsSync(filePath) ? filePath : join(publicDir, "index.html");
  const ext = extname(finalPath);
  response.writeHead(200, { "Content-Type": mimeTypes[ext] || "application/octet-stream" });
  createReadStream(finalPath).pipe(response);
}).listen(port, () => {
  console.log(`Resume Intelligence frontend: http://localhost:${port}`);
});
