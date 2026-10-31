import ts from "typescript";
import fs from "node:fs";
import path from "node:path";

const config = ts.readConfigFile("tsconfig.json", ts.sys.readFile);
const parsed = ts.parseJsonConfigFileContent(
  config.config,
  ts.sys,
  process.cwd(),
);
const host = {
  getScriptFileNames: () => parsed.fileNames,
  getScriptVersion: () => "1",
  getScriptSnapshot: (file) =>
    fs.existsSync(file)
      ? ts.ScriptSnapshot.fromString(fs.readFileSync(file, "utf8"))
      : undefined,
  getCurrentDirectory: () => process.cwd(),
  getCompilationSettings: () => parsed.options,
  getDefaultLibFileName: (options) => ts.getDefaultLibFilePath(options),
  fileExists: ts.sys.fileExists,
  readFile: ts.sys.readFile,
  readDirectory: ts.sys.readDirectory,
};
const service = ts.createLanguageService(host);
for (const file of parsed.fileNames) {
  if (!path.resolve(file).startsWith(path.resolve("src") + path.sep)) continue;
  const changes = service.organizeImports(
    { type: "file", fileName: file },
    {},
    {},
  );
  for (const change of changes) {
    let source = fs.readFileSync(change.fileName, "utf8");
    for (const edit of [...change.textChanges].sort(
      (a, b) => b.span.start - a.span.start,
    )) {
      source =
        source.slice(0, edit.span.start) +
        edit.newText +
        source.slice(edit.span.start + edit.span.length);
    }
    fs.writeFileSync(change.fileName, source);
  }
}
