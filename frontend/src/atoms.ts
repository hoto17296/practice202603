import { atomWithRefresh } from "jotai/utils";

import api from "./lib/api";

export const authSessionAtom = atomWithRefresh(async () => {
  const { response, data, error } = await api.GET("/api/auth/session");
  if (response.status === 401) return null;
  if (error) throw error;
  return data;
});
