import { useQuery } from "@tanstack/vue-query"
import { useGateways } from "../container"
import { queryKeys } from "../queryKeys"

export function useMe() {
  const { session } = useGateways()
  return useQuery({ queryKey: queryKeys.me, queryFn: () => session.me(), staleTime: 5 * 60_000 })
}
