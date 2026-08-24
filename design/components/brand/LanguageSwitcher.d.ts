/** EN / ΕΛ / हि / FR segmented switcher; each option is set in its own script. */
export interface LanguageSwitcherProps {
  /** Active language code */
  current: 'en' | 'el' | 'hi' | 'fr';
  /** Order of options; defaults to en,el,hi,fr */
  languages?: Array<'en' | 'el' | 'hi' | 'fr'>;
  /** Button mode callback */
  onChange?: (lang: string) => void;
  /** Link mode: return the URL for a language variant (used on the journal) */
  hrefFor?: (lang: string) => string;
}
