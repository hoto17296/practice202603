import { useAtomValue } from "jotai";

import { authSessionAtom } from "../atoms";
import api, { type ApiSchemaTypes } from "./api";

export function useSession(): ApiSchemaTypes["AuthSession"] {
  const session = useAtomValue(authSessionAtom);
  if (session === null) {
    window.location.href = "/signin";
    // @ts-ignore
    return;
  }
  return session;
}

export async function signout() {
  const { response, error } = await api.POST("/api/auth/signout");
  if (!response.ok) throw error;
  window.location.reload();
}
