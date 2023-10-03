import { Draft07, Draft, JsonSchema } from "json-schema-library";
import { existsSync, readFileSync, writeFileSync } from "fs"

function parse_scalar_schema(draft: Draft, schema: JsonSchema, field: string)
{
  return [[field, schema.type, schema.default, schema.description]];
}

function parse_object_schema(draft: Draft, schema: JsonSchema, field: string)
{
  let result: Array<Array<string>> = [];
  for (const name in schema.properties)
  {
    const child = field.length ? field + "." + name : name;
    result = result.concat(parse_schema_common(draft, schema.properties[name], child));
  }
  return result;
}

function parse_schema_common(draft: Draft, schema: JsonSchema, field: string)
{
  if (schema.type === "object")
  {
    return parse_object_schema(draft, schema, field);
  }
  else
  {
    return parse_scalar_schema(draft, schema, field)
  }
}

if (process.argv.length !== 3)
{
  throw Error("No file specified")
}

const input = process.argv[2];
const draft = new Draft07(JSON.parse(readFileSync(input, "utf-8")));
const entry = draft.getSchema({ pointer: "~1**/ros__parameters" });
const table = parse_schema_common(draft, entry!, "");

const header = ["Parameter Name", "Type", "Default", "Description"]
const widths = header.map(title => title.length);
for (const row of table)
{
  for (const i in widths)
  {
    widths[i] = Math.max(widths[i], row[i].length)
  }
}

const border = widths.map(width => "-".repeat(width))
const matrix = [header, border, ...table];
let content = "";
for (const row of matrix)
{
  for (const i in widths)
  {
    content += "| " + row[i].padEnd(widths[i]) + " ";
  }
  content += "|\n";
}

const output = input.split(".").slice(0, -2).join(".") + ".md";
const source = existsSync(output) ? readFileSync(output, "utf-8") : undefined;
if (source !== content)
{
  writeFileSync(output, content);
  process.exitCode = 1;
}
