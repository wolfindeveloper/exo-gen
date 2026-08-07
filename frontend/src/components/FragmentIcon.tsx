import { FRAGMENT_ICON } from '../lib/stats'

export function FragmentIcon({ className = 'h-3 w-3' }: { className?: string }) {
  return <img src={FRAGMENT_ICON} alt="" className={`${className} object-contain inline-block align-[-0.1em]`} />
}
