/** Two-way toggle: visitor-local time vs Athens authoring time. */
export interface TimezoneToggleProps {
  value: 'local' | 'athens';
  onChange: (tz: 'local' | 'athens') => void;
}
