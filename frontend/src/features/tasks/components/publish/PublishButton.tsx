'use client'

import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { useTranslation } from '@/hooks/useTranslation'
import { publishedContentApi } from '@/apis/published-content'
import { PublishModal } from './PublishModal'

interface PublishButtonProps {
  subtaskId: number
  contentType: 'video' | 'image'
  videoUrl?: string
  videoThumbnail?: string
  videoDuration?: number
  imageUrls?: string[]
}

export function PublishButton({
  subtaskId,
  contentType,
  videoUrl,
  videoThumbnail,
  videoDuration,
  imageUrls,
}: PublishButtonProps) {
  const { t } = useTranslation('publish')
  const [isPublished, setIsPublished] = useState(false)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  // Check publish status on mount
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const result = await publishedContentApi.checkStatus(subtaskId)
        setIsPublished(!!result)
      } catch (error) {
        console.error('Failed to check publish status:', error)
      } finally {
        setIsLoading(false)
      }
    }

    checkStatus()
  }, [subtaskId])

  const handlePublishSuccess = () => {
    setIsPublished(true)
    setIsModalOpen(false)
  }

  if (isLoading) {
    return null
  }

  return (
    <>
      <Button
        variant={isPublished ? 'outline' : 'default'}
        size="sm"
        disabled={isPublished}
        onClick={() => setIsModalOpen(true)}
        className="h-11 min-w-[44px]"
      >
        {isPublished
          ? t('already_published')
          : t('publish_button', {
              type: contentType === 'video' ? 'video' : 'image',
            })}
      </Button>

      <PublishModal
        open={isModalOpen}
        onOpenChange={setIsModalOpen}
        subtaskId={subtaskId}
        contentType={contentType}
        videoUrl={videoUrl}
        videoThumbnail={videoThumbnail}
        videoDuration={videoDuration}
        imageUrls={imageUrls}
        onSuccess={handlePublishSuccess}
      />
    </>
  )
}
