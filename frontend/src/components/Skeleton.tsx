interface SkeletonProps {
  variant: 'card' | 'row' | 'circle' | 'text' | 'zone' | 'inventory-item'
  count?: number
  className?: string
}

function ShimmerBlock({ className = '' }: { className?: string }) {
  return <div className={`shimmer rounded-lg ${className}`} />
}

function ZoneSkeleton() {
  return (
    <div className="glass-card p-4 space-y-3">
      <div className="flex justify-between items-start">
        <ShimmerBlock className="h-4 w-32 rounded" />
        <ShimmerBlock className="h-3 w-6 rounded" />
      </div>
      <div className="space-y-1.5">
        <ShimmerBlock className="h-3 w-full rounded" />
        <ShimmerBlock className="h-3 w-3/4 rounded" />
      </div>
      <div className="flex gap-3">
        <ShimmerBlock className="h-3 w-12 rounded" />
        <ShimmerBlock className="h-3 w-10 rounded" />
        <ShimmerBlock className="h-3 w-10 rounded" />
      </div>
      <div className="flex gap-1.5">
        <ShimmerBlock className="h-5 w-16 rounded-full" />
        <ShimmerBlock className="h-5 w-14 rounded-full" />
        <ShimmerBlock className="h-5 w-18 rounded-full" />
        <ShimmerBlock className="h-5 w-12 rounded-full" />
      </div>
    </div>
  )
}

function InventoryItemSkeleton() {
  return (
    <div className="glass-card p-3 flex items-center gap-3">
      <ShimmerBlock className="shrink-0 w-8 h-8 rounded-lg" />
      <div className="flex-1 min-w-0 space-y-1.5">
        <div className="flex items-center gap-1.5">
          <ShimmerBlock className="h-4 w-24 rounded" />
          <ShimmerBlock className="h-4 w-6 rounded" />
        </div>
        <ShimmerBlock className="h-3 w-20 rounded" />
      </div>
      <ShimmerBlock className="shrink-0 w-8 h-6 rounded" />
    </div>
  )
}

function RowSkeleton() {
  return (
    <div className="glass-card p-3 flex items-center gap-3">
      <ShimmerBlock className="shrink-0 w-10 h-10 rounded-full" />
      <div className="flex-1 space-y-2">
        <ShimmerBlock className="h-4 w-3/4 rounded" />
        <ShimmerBlock className="h-3 w-1/2 rounded" />
      </div>
      <ShimmerBlock className="shrink-0 w-12 h-5 rounded" />
    </div>
  )
}

const variantMap = {
  card: <ShimmerBlock className="h-[120px] w-full rounded-xl" />,
  row: <RowSkeleton />,
  circle: <ShimmerBlock className="w-12 h-12 rounded-full" />,
  text: <ShimmerBlock className="h-4 w-full rounded" />,
  zone: <ZoneSkeleton />,
  'inventory-item': <InventoryItemSkeleton />,
} as const

export function Skeleton({ variant, count = 1, className = '' }: SkeletonProps) {
  return (
    <div className={className}>
      {Array.from({ length: count }, (_, i) => (
        <div key={i} className={count > 1 && variant !== 'text' ? (variant === 'zone' ? 'mb-3' : 'mb-2') : ''}>
          {variantMap[variant]}
        </div>
      ))}
    </div>
  )
}
