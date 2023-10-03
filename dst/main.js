"use strict";
var __spreadArray = (this && this.__spreadArray) || function (to, from, pack) {
    if (pack || arguments.length === 2) for (var i = 0, l = from.length, ar; i < l; i++) {
        if (ar || !(i in from)) {
            if (!ar) ar = Array.prototype.slice.call(from, 0, i);
            ar[i] = from[i];
        }
    }
    return to.concat(ar || Array.prototype.slice.call(from));
};
Object.defineProperty(exports, "__esModule", { value: true });
var json_schema_library_1 = require("json-schema-library");
var fs_1 = require("fs");
function parse_scalar_schema(draft, schema, field) {
    return [[field, schema.type, schema.default, schema.description]];
}
function parse_object_schema(draft, schema, field) {
    var result = [];
    for (var name_1 in schema.properties) {
        var child = field.length ? field + "." + name_1 : name_1;
        result = result.concat(parse_schema_common(draft, schema.properties[name_1], child));
    }
    return result;
}
function parse_schema_common(draft, schema, field) {
    if (schema.type === "object") {
        return parse_object_schema(draft, schema, field);
    }
    else {
        return parse_scalar_schema(draft, schema, field);
    }
}
if (process.argv.length !== 3) {
    throw Error("No file specified");
}
var input = process.argv[2];
var draft = new json_schema_library_1.Draft07(JSON.parse((0, fs_1.readFileSync)(input, "utf-8")));
var entry = draft.getSchema({ pointer: "~1**/ros__parameters" });
var table = parse_schema_common(draft, entry, "");
var header = ["Parameter Name", "Type", "Default", "Description"];
var widths = header.map(function (title) { return title.length; });
for (var _i = 0, table_1 = table; _i < table_1.length; _i++) {
    var row = table_1[_i];
    for (var i in widths) {
        widths[i] = Math.max(widths[i], row[i].length);
    }
}
var border = widths.map(function (width) { return "-".repeat(width); });
var matrix = __spreadArray([header, border], table, true);
var content = "";
for (var _a = 0, matrix_1 = matrix; _a < matrix_1.length; _a++) {
    var row = matrix_1[_a];
    for (var i in widths) {
        content += "| " + row[i].padEnd(widths[i]) + " ";
    }
    content += "|\n";
}
var output = input.split(".").slice(0, -2).join(".") + ".md";
var source = (0, fs_1.existsSync)(output) ? (0, fs_1.readFileSync)(output, "utf-8") : undefined;
if (source !== content) {
    (0, fs_1.writeFileSync)(output, content);
    process.exitCode = 1;
}
