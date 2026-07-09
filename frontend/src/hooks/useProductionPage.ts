import { useCallback, useEffect, useState } from 'react'
import { getProductionPlan, uploadProductionAsset } from '../api/production'
import type { ProductionPlan } from '../types/production'

type UseProductionPageState = {
  plan: ProductionPlan | null
  isLoading: boolean
  isUploadingAssetKey: string | null
  error: string | null
  reload: () => Promise<void>
  uploadAsset: (
    role: string,
    referenceTag: string,
    requirementNote: string,
    file: File,
  ) => Promise<void>
}

export function useProductionPage(shotId: string): UseProductionPageState {
  const [plan, setPlan] = useState<ProductionPlan | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isUploadingAssetKey, setIsUploadingAssetKey] = useState<string | null>(
    null,
  )
  const [error, setError] = useState<string | null>(null)

  const loadPlan = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    try {
      const nextPlan = await getProductionPlan(shotId)
      setPlan(nextPlan)
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : '加载失败')
    } finally {
      setIsLoading(false)
    }
  }, [shotId])

  useEffect(() => {
    void loadPlan()
  }, [loadPlan])

  async function uploadAsset(
    role: string,
    referenceTag: string,
    requirementNote: string,
    file: File,
  ) {
    if (!plan) {
      return
    }

    const assetKey = `${role}:${referenceTag}`
    setIsUploadingAssetKey(assetKey)
    setError(null)

    try {
      await uploadProductionAsset({
        productionTaskId: plan.task_id,
        role,
        referenceTag,
        requirementNote,
        file,
      })
      const refreshedPlan = await getProductionPlan(shotId)
      setPlan(refreshedPlan)
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : '上传失败')
    } finally {
      setIsUploadingAssetKey(null)
    }
  }

  return {
    plan,
    isLoading,
    isUploadingAssetKey,
    error,
    reload: loadPlan,
    uploadAsset,
  }
}
