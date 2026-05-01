import createClient from "openapi-fetch";

import type { components, paths } from "../api-spec";

const api = createClient<paths>();

export default api;

export type ApiSchemaTypes = components["schemas"];
