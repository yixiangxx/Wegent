'use client'

import { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { useTranslation } from '@/hooks/useTranslation'
import { publishedContentApi } from '@/apis/published-content'
import { toast } from 'sonner'
import { VideoPlayer } from '../message/VideoPlayer'
import { ImageGallery } from '../message/ImageGallery'
import { useIsMobile } from '@/features/layout/hooks/useMediaQuery'

interface PublishModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  subtaskId: number
  contentType: 'video' | 'image'
  videoUrl?: string
  videoThumbnail?: string
  videoDuration?: number
  imageUrls?: string[]
  onSuccess: () => void
}

export function PublishModal({
  open,
  onOpenChange,
  subtaskId,
  contentType,
  videoUrl,
  videoThumbnail,
  videoDuration,
  imageUrls,
  onSuccess,
}: PublishModalProps) {
  const { t } = useTranslation('publish')
  const isMobile = useIsMobile()
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async () => {
    if (!title.trim()) {
      toast.error(t('error.title_required'))
      return
    }

    console.log('[PublishModal] Submitting:', {
      subtask_id: subtaskId,
      content_type: contentType,
      title: title.trim(),
      description: description.trim() || undefined,
    })

    setIsSubmitting(true)

    try {
      await publishedContentApi.publish({
        subtask_id: subtaskId,
        content_type: contentType,
        title: title.trim(),
        description: description.trim() || undefined,
      })

      toast.success(t('success.published'), {
        description: t('success.published_description'),
      })

      onSuccess()
    } catch (error: any) {
      console.error('[PublishModal] Failed to publish:', error)

      // Show more detailed error message
      if (error?.status === 401) {
        toast.error(t('error.publish_failed'), {
          description: 'Authentication required. Please log in again.',
        })
      } else if (error?.message) {
        toast.error(t('error.publish_failed'), {
          description: error.message,
        })
      } else {
        toast.error(t('error.publish_failed'))
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className={`${isMobile ? 'max-w-[95vw]' : 'max-w-4xl'} max-h-[90vh] overflow-y-auto`}
      >
        <DialogHeader>
          <DialogTitle>{t('modal.title')}</DialogTitle>
        </DialogHeader>

        <div
          className={`${isMobile ? 'flex flex-col space-y-4' : 'grid grid-cols-2 gap-6'}`}
        >
          {/* Preview Section */}
          <div className="space-y-2">
            <Label>{t('modal.preview')}</Label>
            <div className="rounded-lg border border-border overflow-hidden bg-surface">
              {contentType === 'video' && videoUrl ? (
                <VideoPlayer
                  videoUrl={videoUrl}
                  thumbnail={videoThumbnail}
                  duration={videoDuration}
                />
              ) : contentType === 'image' && imageUrls && imageUrls.length > 0 ? (
                <ImageGallery images={imageUrls.map((url) => ({ url }))} />
              ) : (
                <div className="flex items-center justify-center h-48 text-text-muted">
                  No preview available
                </div>
              )}
            </div>
          </div>

          {/* Form Section */}
          <div className="space-y-4">
            {/* Title */}
            <div className="space-y-2">
              <Label htmlFor="title">{t('modal.title_label')}</Label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder={t('modal.title_placeholder')}
                maxLength={200}
                required
              />
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="description">{t('modal.description_label')}</Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder={t('modal.description_placeholder')}
                maxLength={2000}
                rows={4}
              />
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isSubmitting}
          >
            {t('common:actions.cancel')}
          </Button>
          <Button
            variant="primary"
            onClick={handleSubmit}
            disabled={isSubmitting || !title.trim()}
          >
            {isSubmitting ? t('modal.publishing') : t('modal.publish_button')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
