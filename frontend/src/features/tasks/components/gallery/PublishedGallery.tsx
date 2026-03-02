'use client'

import { useEffect, useState } from 'react'
import { Heart, Sparkles, Video } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useTranslation } from '@/hooks/useTranslation'
import { publishedContentApi, PublishedWork } from '@/apis/published-content'

export function PublishedGallery() {
  const { t } = useTranslation('publish')
  const [works, setWorks] = useState<PublishedWork[]>([])
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(true)
  const [isLoading, setIsLoading] = useState(false)

  const loadWorks = async (currentPage: number, reset: boolean = false) => {
    if (isLoading) return

    setIsLoading(true)

    try {
      const response = await publishedContentApi.list({
        page: currentPage,
        page_size: 20,
      })

      if (reset) {
        setWorks(response.items)
      } else {
        setWorks((prev) => [...prev, ...response.items])
      }

      setHasMore(response.items.length === 20)
    } catch (error) {
      console.error('Failed to load published works:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // Load initial data
  useEffect(() => {
    setPage(1)
    setWorks([])
    setHasMore(true)
    loadWorks(1, true)
  }, [])

  const handleLoadMore = () => {
    const nextPage = page + 1
    setPage(nextPage)
    loadWorks(nextPage, false)
  }

  const handleLike = async (workId: number) => {
    // TODO: Implement like API call
    console.log('Like work:', workId)
    // Update local state optimistically
    setWorks((prev) =>
      prev.map((work) =>
        work.id === workId ? { ...work, like_count: work.like_count + 1 } : work
      )
    )
  }

  const handleCreateSimilar = (work: PublishedWork) => {
    // TODO: Navigate to generate page with pre-filled prompt
    console.log('Create similar work:', work.prompt)
  }

  const getThumbnail = (work: PublishedWork): string | null => {
    if (work.content_type === 'video') {
      return work.video_thumbnail || null
    } else if (work.content_type === 'image' && work.image_urls && work.image_urls.length > 0) {
      return work.image_urls[0]
    }
    return null
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">{t('gallery.title')}</h2>

      {works.length === 0 && !isLoading ? (
        <div className="text-center py-12 text-text-muted">{t('gallery.no_works')}</div>
      ) : (
        <>
          {/* Grid Layout */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {works.map((work) => {
              const thumbnail = getThumbnail(work)

              return (
                <div
                  key={work.id}
                  className="group relative bg-surface border border-border rounded-lg overflow-hidden cursor-pointer transition-shadow hover:shadow-lg"
                >
                  {/* Thumbnail */}
                  <div className="relative aspect-square overflow-hidden bg-bg-muted">
                    {thumbnail ? (
                      <img
                        src={thumbnail}
                        alt={work.title}
                        className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-text-muted">
                        {t('gallery.no_thumbnail')}
                      </div>
                    )}

                    {/* Video Badge */}
                    {work.content_type === 'video' && (
                      <div className="absolute top-2 right-2 bg-black/60 backdrop-blur-sm rounded-full p-1.5">
                        <Video className="w-4 h-4 text-white" />
                      </div>
                    )}

                    {/* Hover Overlay with Info */}
                    <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                      <div className="absolute inset-x-0 bottom-0 p-3 flex items-end justify-between">
                        {/* Username */}
                        <div className="text-white text-xs font-medium truncate flex-1">
                          {work.username || 'Anonymous'}
                        </div>

                        {/* Action Buttons */}
                        <div className="flex items-center gap-2 ml-2">
                          {/* Create Similar */}
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleCreateSimilar(work)
                            }}
                            className="h-7 w-7 flex items-center justify-center rounded-full bg-white/20 hover:bg-white/30 backdrop-blur-sm transition-colors"
                            title={t('gallery.create_similar')}
                          >
                            <Sparkles className="w-4 h-4 text-white" />
                          </button>

                          {/* Like Button */}
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleLike(work.id)
                            }}
                            className="h-7 px-2 flex items-center gap-1 rounded-full bg-white/20 hover:bg-white/30 backdrop-blur-sm transition-colors"
                            title={t('gallery.like')}
                          >
                            <Heart className="w-4 h-4 text-white" />
                            <span className="text-xs text-white font-medium">
                              {work.like_count}
                            </span>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Title (always visible) */}
                  <div className="p-2">
                    <h3 className="text-sm font-medium text-text-primary line-clamp-2">
                      {work.title}
                    </h3>
                  </div>
                </div>
              )
            })}
          </div>

          {hasMore && (
            <div className="flex justify-center pt-4">
              <Button
                variant="outline"
                onClick={handleLoadMore}
                disabled={isLoading}
                className="h-11 min-w-[44px]"
              >
                {isLoading ? t('common:loading') : t('gallery.load_more')}
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
