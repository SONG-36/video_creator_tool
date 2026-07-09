import type { DashboardMetric, RecentProject } from '../types/dashboard'

type DashboardData = {
  metrics: DashboardMetric[]
  recentProjects: RecentProject[]
}

const dashboardData: DashboardData = {
  metrics: [
    { label: '总项目数', value: 12, accent: '#d97706' },
    { label: '待审核镜头', value: 8, accent: '#ef4444' },
    { label: '等待素材任务', value: 5, accent: '#0f766e' },
    { label: '生成中任务', value: 2, accent: '#2563eb' },
  ],
  recentProjects: [
    {
      id: 'PJT-001',
      name: '洗地机首发演示',
      product: '智能洗地机',
      stage: 'AI生产准备',
      status: '等待素材',
      updatedAt: '今天 09:30',
    },
    {
      id: 'PJT-002',
      name: '厨房清洁剂短片',
      product: '厨房清洁剂',
      stage: 'Storyboard审核',
      status: '待审核',
      updatedAt: '今天 08:10',
    },
    {
      id: 'PJT-003',
      name: '车载吸尘器开箱',
      product: '车载吸尘器',
      stage: '视频生成',
      status: '生成中',
      updatedAt: '昨天 21:40',
    },
  ],
}

export function useDashboardMetrics(): DashboardData {
  return dashboardData
}
