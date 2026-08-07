import { XGEN_ICON } from '../lib/stats'

export function XGenIcon({ className = 'h-3 w-3' }: { className?: string }) {
  return <img src={XGEN_ICON} alt="" className={`${className} object-contain inline-block align-[-0.1em]`} />
}
