import { post, get } from './api'
import type { ExpeditionRead, CraftResponse, ArtifactRead } from '../types'

export async function startExpedition(
  ship_slug: string,
  tier: number,
  fuel_slug: string,
  overdrive_mode: string = 'stable'
): Promise<ExpeditionRead> {
  return post<ExpeditionRead>('/expeditions/start', {
    ship_slug,
    tier,
    fuel_slug,
    overdrive_mode,
  })
}

export async function getActiveExpeditions(): Promise<ExpeditionRead[]> {
  return get<ExpeditionRead[]>('/expeditions/active')
}

export async function getExpedition(id: string): Promise<ExpeditionRead> {
  return get<ExpeditionRead>(`/expeditions/${id}`)
}

export async function craftArtifact(
  domain_slug: string,
  essences: string[],
  xgen_amount: number
): Promise<CraftResponse> {
  return post<CraftResponse>('/laboratory/craft', {
    domain_slug,
    essences,
    xgen_amount,
  })
}

export async function getArtifacts(): Promise<ArtifactRead[]> {
  return get<ArtifactRead[]>('/artifacts')
}

export async function stakeArtifact(artifactId: string): Promise<{ artifact_id: string; staked: boolean; message: string }> {
  return post(`/artifacts/${artifactId}/stake`, {})
}

export async function unstakeArtifact(artifactId: string): Promise<{ artifact_id: string; staked: boolean; message: string }> {
  return post(`/artifacts/${artifactId}/unstake`, {})
}

export async function claimYield(artifactId: string): Promise<{ artifact_id: string; claimed_amount: number; new_accumulated: number }> {
  return post(`/artifacts/${artifactId}/claim-yield`, {})
}

export async function calibrateArtifact(artifactId: string): Promise<{ artifact_id: string; cycles_remaining: number; status: string; xgen_cost: number; resource_cost_slug: string }> {
  return post(`/artifacts/${artifactId}/calibrate`, {})
}
