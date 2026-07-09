export function formatMetricValue(value: number): string {
  return new Intl.NumberFormat('zh-CN').format(value)
}
