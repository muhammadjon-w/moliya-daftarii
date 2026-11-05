// Komponentlar Telegram SDK'ga shu composable orqali murojaat qiladi (plugins/telegram'ni to'g'ridan-to'g'ri emas).
import { telegram } from "@/plugins/telegram"

export function useTelegram() {
  return telegram
}
