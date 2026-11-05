// Server xatolarining ilova ichidagi ko'rinishi (infrastructure shu klassni tashlaydi).
import type { Access } from "@/domain/types"

export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
    readonly fields: Record<string, string[]> | null = null,
    readonly access: Access | null = null,
  ) {
    super(message)
    this.name = "ApiError"
  }

  /** Obuna tugagan: yozish taqiqlangan. */
  get subscriptionRequired(): boolean {
    return this.status === 402
  }

  get unauthorized(): boolean {
    return this.status === 401 || this.status === 403
  }
}
