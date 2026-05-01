import { atom } from "jotai";

import api, { type ApiSchemaTypes } from "./lib/api";

export const authSessionAtom = atom<Promise<ApiSchemaTypes["AuthSession"] | null>>(async () => {
  const { response, data, error } = await api.GET("/api/auth/session");
  if (response.status === 401) return null;
  if (error) throw error;
  return data;
});
