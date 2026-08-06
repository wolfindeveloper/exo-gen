export function formatDuration(seconds: number): string {
  const totalMinutes = Math.round(seconds / 60)
  const totalHours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60

  if (totalHours >= 24) {
    const days = Math.floor(totalHours / 24)
    const hours = totalHours % 24
    if (hours === 0) return `${days}д`
    return `${days}д ${hours}ч`
  }

  if (totalHours > 0) {
    if (minutes === 0) return `${totalHours}ч`
    return `${totalHours}ч ${minutes}м`
  }

  return `${totalMinutes}м`
}
