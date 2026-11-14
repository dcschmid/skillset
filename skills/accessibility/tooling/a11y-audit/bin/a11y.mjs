#!/usr/bin/env node
// a11y launcher — Node >=22.18 type-stripping runs src/cli.ts directly.
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
const here = dirname(fileURLToPath(import.meta.url));
await import(join(here, '..', 'src', 'cli.ts'));
