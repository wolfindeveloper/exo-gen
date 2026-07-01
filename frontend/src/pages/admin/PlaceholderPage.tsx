interface PlaceholderPageProps {
  title: string
}

export function PlaceholderPage({ title }: PlaceholderPageProps) {
  return (
    <div className="flex items-center justify-center h-full">
      <div className="text-center">
        <p className="text-4xl mb-3 opacity-30">🚧</p>
        <p className="text-gray-500 text-lg font-medium">{title}</p>
        <p className="text-gray-600 text-sm mt-1">Раздел в разработке</p>
      </div>
    </div>
  )
}
