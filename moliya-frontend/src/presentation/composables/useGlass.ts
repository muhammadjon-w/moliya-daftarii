// "Liquid Glass": panel ustidagi yaltirash barmoq yoki sichqoncha ortidan yuradi (CSS --mx/--my).
import { onBeforeUnmount, onMounted } from "vue"

const SELECTOR = ".band, .dpanel, .rp-card, .rp-panel, .panel, .stat, .sub-card"

export function useGlassPointer() {
  let raf = 0
  let last: PointerEvent | null = null
  const run = () => {
    raf = 0
    const target = last?.target as Element | null
    const el = target?.closest?.(SELECTOR) as HTMLElement | null
    if (!el || !last) return
    const r = el.getBoundingClientRect()
    if (!r.width || !r.height) return
    el.style.setProperty("--mx", (((last.clientX - r.left) / r.width) * 100).toFixed(1) + "%")
    el.style.setProperty("--my", (((last.clientY - r.top) / r.height) * 100).toFixed(1) + "%")
  }
  const move = (e: PointerEvent) => {
    last = e
    if (!raf) raf = requestAnimationFrame(run)
  }
  onMounted(() => {
    document.addEventListener("pointermove", move, { passive: true })
    document.addEventListener("pointerdown", move, { passive: true })
  })
  onBeforeUnmount(() => {
    document.removeEventListener("pointermove", move)
    document.removeEventListener("pointerdown", move)
    cancelAnimationFrame(raf)
  })
}
