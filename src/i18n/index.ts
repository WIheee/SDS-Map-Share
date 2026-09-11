import { createI18n } from 'vue-i18n'
import type { Composer } from 'vue-i18n'

export const SUPPORT_LOCALES = [
  'zh-CN',
  'zh-TW',
  'en-US',
  'en-GB',
  'ja',
  'ko',
  'fr',
  'de',
  'es',
  'ru',
] as const

export type SupportedLocale = (typeof SUPPORT_LOCALES)[number]

export const DEFAULT_LOCALE: SupportedLocale = 'zh-CN'

const loadedLocales = new Set<string>()

export const i18n = createI18n({
  legacy: false,
  locale: DEFAULT_LOCALE,
  fallbackLocale: 'en-US',
  messages: {},
})

function detectBrowserLocale(): SupportedLocale {
  const navLang = navigator.language || (navigator as any).userLanguage || ''
  if (SUPPORT_LOCALES.includes(navLang as SupportedLocale)) {
    return navLang as SupportedLocale
  }
  const short = navLang.split('-')[0]
  if (short === 'zh') {
    return navLang.includes('TW') || navLang.includes('HK') ? 'zh-TW' : 'zh-CN'
  }
  if (short === 'en') {
    return navLang.includes('GB') ? 'en-GB' : 'en-US'
  }
  const found = SUPPORT_LOCALES.find((l) => l.startsWith(short + '-') || l === short)
  return found ?? DEFAULT_LOCALE
}

async function loadLocaleMessages(locale: string): Promise<void> {
  if (loadedLocales.has(locale)) return
  try {
    const response = await fetch(`${import.meta.env.BASE_URL}language/${locale}.json`)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const messages = await response.json()
    i18n.global.setLocaleMessage(locale, messages)
    loadedLocales.add(locale)
  } catch (e) {
    console.warn(`[i18n] Failed to load locale ${locale}:`, e)
  }
}

export async function setLocale(locale: SupportedLocale): Promise<void> {
  await loadLocaleMessages(locale)
  const composer = i18n.global as unknown as Composer
  composer.locale.value = locale
  document.querySelector('html')?.setAttribute('lang', locale)
  try {
    localStorage.setItem('locale', locale)
  } catch {
    /* ignore */
  }
}

export async function initI18n(): Promise<void> {
  const saved = (() => {
    try {
      return localStorage.getItem('locale') as SupportedLocale | null
    } catch {
      return null
    }
  })()
  const locale = saved && SUPPORT_LOCALES.includes(saved) ? saved : detectBrowserLocale()
  await setLocale(locale)
}
