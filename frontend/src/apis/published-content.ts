// SPDX-FileCopyrightText: 2025 Weibo, Inc.
//
// SPDX-License-Identifier: Apache-2.0

import { apiClient } from './client'

// Published Content Request/Response Types
export interface PublishContentRequest {
  subtask_id: number
  content_type: 'video' | 'image'
  title: string
  description?: string
}

export interface PublishedWork {
  id: number
  user_id: number
  subtask_id: number
  attachment_id: number
  content_type: 'video' | 'image'
  title: string
  description: string | null
  prompt: string | null
  view_count: number
  like_count: number
  is_active: boolean
  is_featured: boolean
  created_at: string
  updated_at: string
  username: string | null
  avatar: string | null
  video_url: string | null
  video_thumbnail: string | null
  video_duration: number | null
  image_urls: string[] | null
}

export interface PublishedWorksListResponse {
  items: PublishedWork[]
  total: number
  page: number
  page_size: number
}

// Published Content API
export const publishedContentApi = {
  // Publish content to gallery
  publish: (data: PublishContentRequest) =>
    apiClient.post<PublishedWork>('/published-contents', data),

  // List published works (public, no auth)
  list: (params?: {
    content_type?: 'video' | 'image'
    page?: number
    page_size?: number
  }) => {
    const queryParams = new URLSearchParams()
    if (params?.content_type) queryParams.set('content_type', params.content_type)
    if (params?.page) queryParams.set('page', params.page.toString())
    if (params?.page_size) queryParams.set('page_size', params.page_size.toString())

    const queryString = queryParams.toString()
    const url = queryString ? `/published-contents?${queryString}` : '/published-contents'

    return apiClient.get<PublishedWorksListResponse>(url)
  },

  // Check if content is already published
  checkStatus: (subtaskId: number) =>
    apiClient.get<PublishedWork | null>(`/published-contents/check/${subtaskId}`),
}
